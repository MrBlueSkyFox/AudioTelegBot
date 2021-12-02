
from pydub import AudioSegment
import os

class AudioConvertor:
    def __init__(self) -> None:
        pass
    
    def convert(self,path_ogg,path_wav):
        ogg_version = AudioSegment.from_ogg(path_ogg).export(path_wav, format="wav")
        wav_version = AudioSegment.from_wav(path_wav).set_frame_rate(16000)
        wav_version.export(path_wav,format='wav')
        os.remove(path_ogg)


