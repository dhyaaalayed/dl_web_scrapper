from datetime import datetime



class Notifier:

    def __init__(self):
        self.new_installed_addresses = []
        self.new_gbgs_addresses = []
        self.failed_uploaded_files = []
        self.new_bulk_addresses = []
        self.failed_matching_bulk_addresses = []
        self.failed_updating_bvhs = []

    def add_new_gbgs_address(self, new_address: str) -> None:
        self.new_gbgs_addresses.append(new_address)

    def add_new_installed_address(self, new_installed_address: str) -> None:
        self.new_installed_addresses.append(new_installed_address)

    def add_failed_uploaded_file(self, failed_uploaded_file: str) -> None:
        self.failed_uploaded_files.append(failed_uploaded_file)

    def add_failed_updated_bvh(self, failed_updated_bvh: str) -> None:
        self.failed_updating_bvhs.append(failed_updated_bvh)

    def get_notifications_as_string(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Email Title:
        notifications = ["GBGS Run at {}".format(current_time)]
        notifications.append("_" * 40)
        # New addresses:
        if len(self.new_gbgs_addresses) > 0:
            notifications.append("Neue Adresse/n wurde/n in GBGS hinzugefügt:\n")
            notifications += self.new_gbgs_addresses + ["\n", "_" * 40, "\n"]

        if len(self.new_installed_addresses) > 0:
            notifications.append("HTN kann für diese Adresse/en durchgeführt werden. Die Auskundung wurde durchgeführt.\n")
            notifications += self.new_installed_addresses + ["\n", "_" * 40, "\n"]

        if len(self.failed_uploaded_files) > 0:
            notifications.append("Uploading these files has been failed!\n")
            notifications += self.failed_uploaded_files + ["\n", "_" * 40, "\n"]

        if len(self.new_bulk_addresses) > 0:
            notifications.append("Adding these Buld Addresses!\n")
            notifications += self.new_bulk_addresses + ["\n", "_" * 40, "\n"]

        if len(self.failed_matching_bulk_addresses) > 0:
            notifications.append("These bulk addresses have not matched any of the montage addresses!\n")
            notifications += self.failed_matching_bulk_addresses + ["\n", "_" * 40, "\n"]

        if len(self.failed_updating_bvhs) > 0:
            notifications.append("These bvhs have not updated: ")
            notifications += self.failed_updating_bvhs + ["\n", "_" * 40, "\n"]


        return "\n".join(notifications)

    def there_is_new_changes(self) -> bool:
        """
            We use this function to test to decide to send an email or not
        """
        return len(self.failed_uploaded_files) \
               + len(self.new_installed_addresses) \
               + len(self.new_gbgs_addresses) \
               + len(self.new_bulk_addresses) \
               + len(self.failed_matching_bulk_addresses) \
               + len(self.failed_updating_bvhs) > 0


NOTIFIER = Notifier()
