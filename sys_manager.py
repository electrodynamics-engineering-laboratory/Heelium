def get_storage_gigabytes():
	total, free, avaliable = shutil.disk_usage(__file__)
	return (total/10**9, free/10**9, avaliable/10**9)