import asyncio
import asyncmy
import pytz
import re
import traceback
from datetime import datetime, timedelta

# Local imports
from modules.mongodb_connector import MongoDBConnector
from modules.crypto_utils import decrypt_password
from modules.time_utils import get_kst_time
from modules.json_loader import load_json
from config import MONGODB_SLOWLOG_COLLECTION_NAME, EXEC_TIME

# Definitions
collection = MongoDBConnector.get_database()[MONGODB_SLOWLOG_COLLECTION_NAME]
pid_time_cache = {}


async def query_mysql_instance(instance_name, pool, collection, status_dict):
    try:
        current_pids = set()
        sql_query = """SELECT `ID`, `DB`, `USER`, `HOST`, `TIME`, `INFO`
                        FROM `information_schema`.`PROCESSLIST`
                        WHERE info IS NOT NULL
                        AND DB not in ('information_schema', 'mysql', 'performance_schema')
                        AND USER not in ('monitor', 'rdsadmin')
                        ORDER BY `TIME` DESC"""

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql_query)
                result = await cur.fetchall()

                for row in result:
                    pid, db, user, host, time, info = row
                    current_pids.add(pid)

                    if time >= EXEC_TIME:
                        cache_data = pid_time_cache.setdefault((instance_name, pid), {'max_time': 0})
                        cache_data['max_time'] = max(cache_data['max_time'], time)
                        # Debug
                        # print(f"{get_kst_time()} - Data cached for instance: {instance_name},
                        # pid: {pid},
                        # max_time: {cache_data['max_time']}")

                        if 'start' not in cache_data:
                            utc_now = datetime.now(pytz.utc)
                            utc_start_timestamp = int((utc_now - timedelta(seconds=EXEC_TIME)).timestamp())
                            utc_start_datetime = datetime.fromtimestamp(utc_start_timestamp, pytz.utc)
                            cache_data['start'] = utc_start_datetime

                        info_cleaned = re.sub(' +', ' ', info).encode('utf-8', 'ignore').decode('utf-8')
                        info_cleaned = re.sub(r'[\n\t\r]+', ' ', info_cleaned).strip()

                        cache_data['details'] = {
                            'instance': instance_name,
                            'db': db,
                            'pid': pid,
                            'user': user,
                            'host': host,
                            'time': time,
                            'sql_text': info_cleaned
                        }

                for (instance, pid), cache_data in list(pid_time_cache.items()):
                    if pid not in current_pids and instance == instance_name:
                        data_to_insert = cache_data['details']
                        data_to_insert['time'] = cache_data['max_time']
                        data_to_insert['start'] = cache_data['start']

                        utc_now = datetime.now(pytz.utc)
                        data_to_insert['end'] = utc_now

                        # DEBUG
                        # print(f"{get_kst_time()} - {data_to_insert}")
                        await collection.insert_one(data_to_insert)

                        del pid_time_cache[(instance, pid)]

        await asyncio.sleep(1)
        status_dict[instance_name] = "Success"
    except Exception as e:
        status_dict[instance_name] = f"Failed: {e}"


async def run_mysql_slow_queries():
    pools = {}
    instance_status = {}
    max_retries = 3

    try:
        MongoDBConnector.initialize()

        instances = load_json("rds_instances.json")

        while True:
            tasks = []
            for instance_data in instances:
                instance_name = instance_data["instance_name"]
                if instance_name in pools and pools[instance_name] is None:
                    continue
                host = instance_data["host"]
                port = instance_data["port"]
                user = instance_data["user"]
                db = instance_data["db"]
                encrypted_password_base64 = instance_data["password"]
                decrypted_password = decrypt_password(encrypted_password_base64)

                if instance_name not in pools:
                    for attempt in range(max_retries):
                        try:
                            pool = await asyncmy.create_pool(
                                host=host, port=port, user=user, password=decrypted_password, db=db
                            )
                            pools[instance_name] = pool
                            print(f"{get_kst_time()} - Connection pool created successfully for {instance_name}")
                            break
                        except Exception as e:
                            print(f"{get_kst_time()} - Attempt {attempt + 1} failed for {instance_name}: {e}")
                            if attempt == max_retries - 1:
                                pools[instance_name] = None
                                print(
                                    f"{get_kst_time()} - Maximum retry attempts reached for {instance_name}. "
                                    f"Skipping this instance.")

                if pools.get(instance_name):
                    tasks.append(query_mysql_instance(instance_name, pools[instance_name], collection, instance_status))

            if tasks:
                await asyncio.gather(*tasks)
            for instance, status in instance_status.items():
                if "Failed" in status:
                    print(f"{get_kst_time()} - Instance {instance} Status: {status}")

            await asyncio.sleep(1)

    except asyncio.CancelledError:
        print("{get_kst_time()} - Async task was cancelled. Cleaning up...")
        for pool_name, pool in pools.items():
            if pool is not None:
                try:
                    await pool.close()
                except Exception as e1:
                    print(f"{get_kst_time()} - An error occurred while closing the pool {pool_name}: {e1}")

        print(f"{get_kst_time()} - Resources have been released and program has been terminated safely.")
        traceback.print_exc()

    except Exception as e2:
        print(f"An error occurred: {e2}")
        traceback.print_exc()

    finally:
        for pool_name, pool in pools.items():
            if pool is not None:
                try:
                    await pool.close()
                except Exception as ex:
                    print(f"{get_kst_time()} - An error occurred while closing the pool {pool_name}: {ex}")

        await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(run_mysql_slow_queries())
