import pyaudio
import mute_alsa

class PyAduioSettings():
	p = pyaudio.PyAudio()
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')

	def return_output_devices(self):
		output_dev = []
		for i in range (0,self.numdevices):
			if self.p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
				# print( "Output Device id " + str(i) +  " - " + self.p.get_device_info_by_host_api_device_index(0,i).get('name'))
				output_dev.append([self.p.get_device_info_by_host_api_device_index(0,i).get("name"), i])
		print(output_dev)
		return output_dev

	def return_input_devices(self):
		input_dev = []
		for i in range (0,self.numdevices):
			if self.p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
				# print( "Input Device id " + str(i) +  " - " + self.p.get_device_info_by_host_api_device_index(0,i).get('name'))
				input_dev.append([self.p.get_device_info_by_host_api_device_index(0,i).get("name"), i])
		print(input_dev)
		return input_dev
	
	def find_default_device(self, device_list):
		for i, sublist in enumerate(device_list):
			# print(sublist)
			if 'default' in sublist:
				return sublist[1]
		return -1

	def find_device_by_number(self, device_list, device_num):
		for i, sublist in enumerate(device_list):
			# print(sublist)
			if device_num == str(sublist[1]):
				return sublist[0]
		return -1


# pyA = PyAduioSettings()
# # pyA.return_input_devices()
# out_dev = pyA.return_output_devices()
# print(out_dev)
# print(pyA.find_device_by_number(out_dev, '2'))


