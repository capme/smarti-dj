from faker import Faker
from faker.providers import BaseProvider
from pickup.models import PickUp

fake = Faker()


class CreatePickUp(BaseProvider):

    @staticmethod
    def create_pickup_data():
        return {
            "package_uuid": fake.name(),
            "package_id": fake.name(),
            "tracking_number": fake.random_int(),
            "package_created_at": fake.date_time()
        }

    @staticmethod
    def create_pickup_to_db():

        pickup = PickUp.objects.create(
            package_uuid="lazada-package-id",
            package_id="MPDS-12456722396-098",
            tracking_number="0300123456781",
            package_created_at="2011-09-01T13:20:30+03:00"
        )

        return pickup

    @staticmethod
    def create_pickup_to_db2():

        pickup = PickUp.objects.create(
            package_uuid="lazada-package-id-1",
            package_id="MPDS-12456722396-098",
            tracking_number="030010405038",
            package_created_at="2016-01-23 23:34:45",
            last_status="FAILED_TO_DELIVER"
        )

        return pickup

    @staticmethod
    def create_pickup_to_db3():
        pickup = PickUp.objects.create(
            package_uuid="",
            package_id="MPDS-12456722396-098",
            tracking_number="030010405038",
            package_created_at="2016-01-23 23:34:45",
            last_status="FAILED_TO_DELIVER"
        )

        return pickup

    @staticmethod
    def create_pickup_another_data():
        return {
            "package_uuid": "lazada-package-id",
            "package_id": "MPDS-12456722396-098",
            "tracking_number": "0300123456781",
            "package_created_at": "2011-09-01T13:20:30+03:00"
        }


class UpdateStatus(BaseProvider):

    @staticmethod
    def return_status():
        return {
            "package_uuid": "lazada-package-id-status",
            "tracking_id": "030010405038-status",
            "status": "FAILED_TO_DELIVER",
            "timestamp": "2016-01-23 23:34:45"
        }

    @staticmethod
    def return_status_completed():
        return {
            "package_uuid": "lazada-package-id-status-completed",
            "tracking_id": "030010405038-status-completed",
            "status": "COMPLETED",
            "timestamp": "2016-01-23 23:34:45"
        }

    @staticmethod
    def create_pickup_status_to_db():
        pickup = PickUp.objects.create(
            package_uuid="lazada-package-id-status",
            package_id="MPDS-12456722396-098-status",
            tracking_number="030010405038-status",
            package_created_at="2011-09-01T13:20:30+03:00"
        )

        return pickup

    @staticmethod
    def create_pickup_status_completed_to_db():
        pickup = PickUp.objects.create(
            package_uuid="lazada-package-id-status-completed",
            package_id="MPDS-12456722396-098-status-completed",
            tracking_number="030010405038-status-completed",
            package_created_at="2011-09-01T13:20:30+03:00"
        )

        return pickup

fake.add_provider(CreatePickUp)
fake.add_provider(UpdateStatus)
