import pyaudio
import mute_alsa

class PyAduioSettings():
	p = pyaudio.PyAudio()
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')

	def return_output_devices(self):
		out_dev = []
		output_dev = []
		for i in range (0,self.numdevices):
			if self.p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
				# print( "Output Device id " + str(i) +  " - " + self.p.get_device_info_by_host_api_device_index(0,i).get('name'))
				out_dev.append([self.p.get_device_info_by_host_api_device_index(0,i).get("name"), i])

		for dev in out_dev:
			devinfo = self.p.get_device_info_by_index(dev[1])
			try:
				if self.p.is_format_supported(44100.0,  # Sample rate
							input_device=devinfo['index'],
							input_channels=1,
							input_format=pyaudio.paInt16):
					print('Yay!')
					output_dev.append(dev)
			except:
				pass
					

		print(output_dev)
		return output_dev

	def return_input_devices(self):
		in_dev = []
		input_dev = []
		for i in range (0,self.numdevices):
			if self.p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
				# print( "Input Device id " + str(i) +  " - " + self.p.get_device_info_by_host_api_device_index(0,i).get('name'))
				in_dev.append([self.p.get_device_info_by_host_api_device_index(0,i).get("name"), i])

		print(in_dev)
		for dev in in_dev:
			devinfo = self.p.get_device_info_by_index(dev[1])
			try:
				if self.p.is_format_supported(44100.0,  # Sample rate
							input_device=devinfo['index'],
							input_channels=1,
							input_format=pyaudio.paInt16):
					print('Yay!')
					input_dev.append(dev)
			except:
				pass
		print(input_dev)
		return input_dev

	# return the name or number of the default device. nameOrNumber - 0 - name, 1 - number
	def find_default_device(self, device_list, nameOrNumber): 
		for i, sublist in enumerate(device_list):
			# print(sublist)
			if 'default' in sublist:
				return sublist[nameOrNumber]
		return -1

	def find_device_by_number(self, device_list, device_num):
		for i, sublist in enumerate(device_list):
			# print(sublist)
			if device_num == str(sublist[1]):
				return sublist[0]
		# if the desired device is not found, return the default device
		return self.find_default_device(device_list, 0)

	def find_number_by_device(self, device_list, device_name):
		for i, sublist in enumerate(device_list):
			# print(sublist)
			if device_name == sublist[0]:
				return sublist[1]	
		return -1

# pyA = PyAduioSettings()
# # pyA.return_input_devices()
# out_dev = pyA.return_output_devices()
# print(out_dev)
# # print(pyA.find_device_by_number(out_dev, '2'))
# print(pyA.find_number_by_device(out_dev, 'HDA NVidia: HDMI 0 (hw:1,3)'))


