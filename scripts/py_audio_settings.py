import pyaudio
import mute_alsa

# Class for getting information about the audio settings of the system
class PyAduioSettings():
	p = pyaudio.PyAudio()
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')

	# Returns a list of output devices. 
	def return_output_devices(self):
		out_dev = []
		output_dev = []
		for i in range (0,self.numdevices):
			if self.p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
				out_dev.append([self.p.get_device_info_by_host_api_device_index(0,i).get("name"), i])

		# print(output_dev)
		return out_dev

	# Returns a list of input devices. The devices have to support 44100Hz sampling rate. 
	# On linux based systems some devices get omited because the default sampling rate is set to the maximum sampling rate.  
	def return_input_devices(self):
		in_dev = []
		input_dev = []
		for i in range (0,self.numdevices):
			if self.p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
				in_dev.append([self.p.get_device_info_by_host_api_device_index(0,i).get("name"), i])

		for dev in in_dev:
			devinfo = self.p.get_device_info_by_index(dev[1])
			try:
				if self.p.is_format_supported(44100.0,  # Sample rate
							input_device=devinfo['index'],
							input_channels=1,
							input_format=pyaudio.paInt16):
					input_dev.append(dev)
			except:
				pass
		print(input_dev)
		return input_dev

	# Return either the index number or name of the default device. nameOrNumber - 0 - name, 1 - number
	def find_default_device(self, device_list, nameOrNumber): 
		for i, sublist in enumerate(device_list):
			# print(sublist)
			if 'default' in sublist:
				return sublist[nameOrNumber]
		return -1

	# Returns the name of the device from device_list based on the device_num
	def find_device_by_number(self, device_list, device_num):
		for i, sublist in enumerate(device_list):
			# print(sublist)
			if device_num == str(sublist[1]):
				return sublist[0]
		# if the desired device is not found, return the default device
		return self.find_default_device(device_list, 0)

	# Returns the device number from the device_list based on the device name
	def find_number_by_device(self, device_list, device_name):
		for i, sublist in enumerate(device_list):
			# print(sublist)
			if device_name == sublist[0]:
				return sublist[1]	
		return -1



