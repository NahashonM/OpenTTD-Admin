
import re



def ctypes_values_list( ctypes_struct):
	values = []
	for field in ctypes_struct._fields_:
		values.append( getattr(ctypes_struct, field[0]) )
	
	return values



def cmd_processor(cmd_str):
	if not cmd_str.startswith("!"):
		return None
	
	cmd_args = re.split(r'\s+(?=(?:[^\'"]*[\'"][^\'"]*[\'"])*[^\'"]*$)', cmd_str[1:])
	if not cmd_args or cmd_args[0] == '':
		return None
	
	return cmd_args
	