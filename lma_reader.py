### Generated from /home/moto/jupyter/2016B/Acqiris/Class-LMAFile.ipynb at 2016/12/10 00:33:58

import struct
import os.path
import numpy as np

class LMAFileReader(object):
    """
    AGAT3で保存された.lmaファイルにアクセスするためのクラス．
    データサイズが可変長のため，結構面倒な処理をしている．
    これを基本クラスとして拡張する．
    
    """
    class LMAChannel(object):
        """
        チャンネルごとの構造体．__slots__を定義して省メモリ化
        メインクラスでこのインスタンスのリストを作成．チャンネルごとに波形データは保持される．
        """
        __slots__ = ['fullscale', 'offset', 'gain', 'baseline','waveform']
        def __init__(self, nbrSamples):
            self.fullscale = 0
            self.offset = 0
            self.gain = 0
            self.baseline = 0
            self.waveform = np.zeros(nbrSamples, dtype=np.float64)
        
    def __init__(self, fileName):
        """
        クラスの初期化：
        ファイルのオープン．lmaのデータ構造に合わせたstructの定義
        引数fileNameはフルパスで与える
        """
        self.fileSize = os.path.getsize(fileName)
        self.lmaFile = open(fileName, 'br')
        # short:h int32:i double:d unsighed int32:I　---Need "="
        # prepare data structure for headers
        self.structFileHeader = struct.Struct("= i h h d i d h d h I I h")
        self.structEachChannel = struct.Struct("= h h d h h i i")
        self.structEvent = struct.Struct("= i d")       
        self.ReadHeader()
        
    def ReadHeader(self):
        """
        ファイルヘッダとチャンネルごとのヘッダの読み込み
        ファイルポインタは先頭
        self.channelがチャンネルごとのデータオブジェクト
        注意！！チャンネルは0から．
        """
        fileHeaderSize = self.structFileHeader.size
        chHeaderSize = self.structEachChannel.size
        self.lmaFile.seek(0)
        headerForFile = self.structFileHeader.unpack_from(self.lmaFile.read(fileHeaderSize))
        # copy file header info to members
        self.headerSize = headerForFile[0] + 4
        self.nbrChannels = headerForFile[1]
        self.nbrBytes = headerForFile[2]
        self.sampInter = headerForFile[3]
        self.nbrSamples = headerForFile[4]
        self.delayTime = round(headerForFile[5], 100)
        self.usedChannel = headerForFile[9]
        # initialize a list of channnel objects
        self.channel = [self.LMAChannel(self.nbrSamples) for i in range(self.nbrChannels)]
        # read and copy infos for each channel
        for i, chan in enumerate(self.channel):
            # check userd channel
            if (self.usedChannel >> i) & 0b1 == 1:
                headerForCh = self.structEachChannel.unpack_from(self.lmaFile.read(chHeaderSize))
                chan.fullscale = headerForCh[0]
                #chan.offset = headerForCh[1]
                chan.gain = headerForCh[2]
                chan.baseline = headerForCh[3]
                
    def GoToFirstWave(self):
        """最初のイベントの位置へファイルポインタを移動"""
        self.lmaFile.seek(self.headerSize)
        
    def LoadWaves(self):
        """
        現在ファイルポインタの位置から，1イベント分の全チャンネルまとめての波形読み込み．
        頭から読んで行っているので，ファイルの最後まで来たらFalseを返す．
        波形はself.channel[ch].waveformにdoubleで保存
        """
        if self.lmaFile.tell() >= self.fileSize:
            return False
        #print("filePos:",self.lmaFile.tell(),self.structEvent.size)
        headerForEvent = self.structEvent.unpack_from(self.lmaFile.read(self.structEvent.size))
        self.tag = headerForEvent[0]
        horpos = headerForEvent[1]
        #print(headerForEvent)
        for ch, chan in enumerate(self.channel):
            if (self.usedChannel >> ch) & 0b1 == 1:
                chan.waveform[:] = 0
                nbrPulse = struct.unpack_from("=h", self.lmaFile.read(2))
                #print(nbrPulse)
                for j in range(nbrPulse[0]):
                    pulseInfo = struct.unpack_from("=ii", self.lmaFile.read(8))
                    firstPointPulse = pulseInfo[0]
                    lengthOfPulse = pulseInfo[1]
                    #print("pulse ch:",ch, pulseInfo)
                    # ----- for 10 / 8bit acqiris must be dtype=np.int16 / np.int8 ----- #
                    data = np.fromfile(self.lmaFile, dtype=np.int16, count=lengthOfPulse)
                    chan.waveform[firstPointPulse:firstPointPulse+lengthOfPulse] \
                        = (data.astype(np.int32) - chan.baseline) * chan.gain
                        
        return True