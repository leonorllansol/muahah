import agents
import os, sys
import pkgutil 

def dynamic_agents_inits_generator():
	CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'
	SUB_DIRS = next(os.walk(CURRENT_DIR))[1]
	for SUB_DIR in SUB_DIRS:
		if SUB_DIR == '__pycache__':
			continue
		SUB_DIRE = CURRENT_DIR + SUB_DIR
		sys.path.append(SUB_DIRE)
		list_dir = os.listdir(SUB_DIRE)
		toWrite = 'import os\nCURRENT_DIR = os.path.dirname(os.path.abspath(__file__))\nos.chdir(CURRENT_DIR)\n'
		toWrite += 'import agents.' + SUB_DIR + '\n'
		if '__init__.py' not in list_dir:
			for file in list_dir:
				if file.endswith('.py'):
					print(toWrite)
					toWrite += 'import agents.' + SUB_DIR + '.' + file[:-3] + '\n'
			f = open(SUB_DIRE + '/__init__.py', 'w+')
			f.write(toWrite)
			f.close()


def dynamic_import_agents(__path__):
	all_modules = []
	for importer, modname, ispkg in pkgutil.walk_packages(path=__path__, prefix=__name__+'.'):
		all_modules.append(modname)
		__import__(modname)
	return all_modules

curr_dir = os.getcwd()

dynamic_agents_inits_generator()
__path__ = pkgutil.extend_path(__path__, __name__)
all_modules = dynamic_import_agents(__path__)

os.chdir(curr_dir)