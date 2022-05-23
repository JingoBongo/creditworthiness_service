import schedule
import time
import general_utils as g
import os
import requests

SYS_SERVICES_TABLE_NAME = 'Sys_Services'
BUSINESS_SERVICES_TABLE_NAME = 'Business_Services'
cur_file_name = os.path.basename(__file__)


def print_c(text):
    print(f"[{cur_file_name}] {str(text)}")


def ping_one(port):
    r = requests.patch(f"http://localhost:{port}{g.LIFE_PING_ENDPOINT_CONTEXT}").status_code
    if r:
        return 'alive'
    return 'false'


def process_service_statuses(services_and_statuses):
    for n in services_and_statuses:
        if n['status'] == 'dead':
            pass # TODO
#             forcibly kill process

#             forcibly start process again

#             delete previous record from DB

#             insert new record to DB


def job():
    print_c("Scheduled life_ping task started..")
    sys_services = g.db_utils.select_from_table(SYS_SERVICES_TABLE_NAME) + g.db_utils.select_from_table(
        BUSINESS_SERVICES_TABLE_NAME)
    services_and_statuses = []
    for i in sys_services:
        service_status = ping_one(i.port)
        services_and_statuses.append({'name': i.name, 'port': i.port, 'pid': i.pid, 'status': service_status})
        short_name = i.name.split('\\')[-1]
        print_c(f"Endpoint {short_name} is {service_status}")
    process_service_statuses(services_and_statuses)
    print_c("Scheduled life_ping task finished")


# schedule.every(5).seconds.do(job)
schedule.every(1).minute.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
