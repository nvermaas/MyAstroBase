from django.core.files.storage import FileSystemStorage

class OverwriteStorage(FileSystemStorage):
    """
    Overwrites file
    """

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name
