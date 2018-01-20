#!/usr/bin/python
# coding: utf8
#########################################################################
# Author: Xinyu.Xiang(John)
# email: zorrohunter@gmail.com
# Created Time: 2009年05月20日 星期三 15时33分55秒
# File Name: umd.py
# Description: 
#########################################################################
import datetime
import struct
import cStringIO
import Image
import zlib
import random

class Chapter(object):
    def _getTitle(self):
        return self.title
    def _setTitle(self,value):
        self.title=value
    Title=property(_getTitle,_setTitle,None,'unicode,title of the chapter')

    def _getContent(self):
        return self.content
    def _setContent(self,value):
        self.content=value
    Content=property(_getContent,_setContent,None,'unicode,content of the chapter')

    def __init__(self,title,content):
        self.title=title
        self.content=content

class UMDFile(object):

    def __init__(self):
    	self.additionalCheck = 0
    	self.author = ''
    	self.chapOff = []
    	self.chapters = []
    	self.cid = 0
    	self.contentLength =0
    	self.cover=None
    	self.day=None
    	self.encoding='utf-16-le'
    	self.gender=''
    	self.month=None
    	self.pgkSeed=0
    	self.publishDate=datetime.datetime.now()
    	self.publisher=''
    	self.title=''
    	self.type=None
    	self.vendor=''
    	self.year=None
    	self.zippedSeg=[]
    	self.arrJpeg=[] 

    def _getArrJpeg(self):
        return self.arrJpeg
    def _setArrJpeg(self,value):
        self.arrJpeg=value
    #ArrJpeg=property(_getArrJpeg,_setArrJpeg,None,'a list of image')
    
    def _getTitle(self):
        return self.title
    def _setTitle(self,value):
        self.title=value
    Title=property(_getTitle,_setTitle,None,'unicode,umd title')

    def _getChapters(self):
        return self.chapters
    def _setChapters(self,value):
        self.chapters=value
    Chapters=property(_getChapters,_setChapters,None,'Chapters,list of Chapter')

    def _getPublisher(self):
        return self.publisher
    def _setPublisher(self,value):
        self.publisher=value
    Publisher=property(_getPublisher,_setPublisher,None,'unicode,Publisher')

    def _getCover(self):
        return self.cover
    def _setCover(self,value):
        self.cover=value
    Cover=property(_getCover,_setCover,None,'Cover: an Image(in module pil), the cover of the book')

    def _getAuthor(self):
        return self.author
    def _setAuthor(self,value):
        self.author=value
    Author=property(_getAuthor,_setAuthor,None,'unicode,Author')


    def read(self,ufile):
        '''
        ufile: binary file-like object
        '''
        self.chapters=[]
        self.arrJpeg=[]
        num1=self._readuint32(ufile)
        if num1 != 0xde9a9b89:
            raise UMDException('wrong header')
        ch1=self._peekchar(ufile)
        while ch1=='#':
            ufile.read(1)
            num2=self._readint16(ufile)
            num3=self._readbyte(ufile)
            num4=self._readbyte(ufile)-5
            self._readSection(num2,num3,num4,ufile)
            ch1=self._peekchar(ufile)
            if num2==0xf1 or num2==10:
                num2=0x84
            while ch1=='$':
                ufile.read(1)
                num5=self._readuint32(ufile)
                num6=self._readuint32(ufile)-9
                #print ufile.tell()
                self._readadditional(num2,num5,num6,ufile)
                ch1=self._peekchar(ufile)
            #print ufile.tell()
        #print ufile.tell()
        ufile.close()
        if self.type=='2':
            return
        extlist=[]
        #print self.zippedSeg
        for zitm in self.zippedSeg:
            extlist.append(zlib.decompress(zitm))
        totalcontent=''.join(extlist)
        for i in xrange(len(self.chapOff)):
            stt=self.chapOff[i]
            if i<len(self.chapOff)-1:
                ed=self.chapOff[i+1]
            else:
                ed=len(totalcontent)
            #print 'stt',stt,'ed',ed,'len(totalcontent)',len(totalcontent)
            self.chapters[i].content=totalcontent[stt:ed].decode(self.encoding)
        self.zippedSeg=[]
        self.publishDate=datetime.datetime(int(self.year),int(self.month),int(self.day))


                
    def _readadditional(self,id,check,length,ufile):
        if id==0x0e:
            self.arrJpeg.append(self._readimg(ufile,length))
            return
        elif id==0x0f:
            return
        elif id==0x81:
            ufile.read(length)
            return
        elif id==130:
            self.cover=self._readimg(ufile,length)
            return
        elif id==0x83:
            self.chapOff=[0]*(length/4)
            num1=0
            while num1 < len(self.chapOff):
                self.chapOff[num1]=self._readint32(ufile)
                num1+=1
            return
        elif id==0x84:
            if self.additionalCheck != check:
                self.zippedSeg.append(ufile.read(length))
                return
            num2=0
            buffer1=ufile.read(length)
            while num2 < len(buffer1):
                num3=ord(buffer1[num2])
                num2+=1
                self.chapters.append(Chapter(buffer1[num2:num2+num3].decode(self.encoding),u''))
                num2+=num3
            return
        else:
            ufile.read(length)
            return
                
        
    def _readimg(self,ufile,length):
        return Image.open(cStringIO.StringIO(ufile.read(length)))
    def _writeimg(self,ufile,img):
        img.save(ufile,'gif')

    def _readbyte(self,ufile):
        return ord(ufile.read(1))
    def _writebyte(self,ufile,b):
        ufile.write(chr(b))
                
    def _readchar(self,ufile):
        return ufile.read(1)
    def _writechar(self,ufile,c):
        ufile.write(c)

    def _peekchar(self,ufile):
        c=ufile.read(1)
        ufile.seek(-1,1)
        return c

    def _readint32(self,ufile):
        return struct.unpack('<i',ufile.read(4))[0]
    def _writeint32(self,ufile,i32):
        ufile.write(struct.pack('<i',i32))

    def _readuint32(self,ufile):
        return struct.unpack('<I',ufile.read(4))[0]
    def _writeuint32(self,ufile,ui32):
        ufile.write(struct.pack('<I',ui32))

    def _readint16(self,ufile):
        return struct.unpack('<h',ufile.read(2))[0]
    def _writeint16(self,ufile,i16):
        ufile.write(struct.pack('<h',i16))

    def _readstr2uni(self,ufile,length):
        return ufile.read(length).decode(self.encoding)
    def _writeuni2str(self,ufile,us):
        ufile.write(us.encode(self.encoding))
            

    def _readSection(self,id,b,length,ufile):
        if id==1:
            self.type=str(self._readbyte(ufile))
            self.pgkSeed=self._readint16(ufile)
            return
        elif id==2:
            self.title= self._readstr2uni(ufile,length) 
            return
        elif id==3:
            self.author= self._readstr2uni(ufile,length)
            return
        elif id==4:
            self.year=self._readstr2uni(ufile,length)
            return
        elif id==5:
            self.month=self._readstr2uni(ufile,length)
            return
        elif id==6:
            self.day=self._readstr2uni(ufile,length)
            return
        elif id==7:
            self.gender=self._readstr2uni(ufile,length)
            return
        elif id==8:
            self.publisher=self._readstr2uni(ufile,length)
            return
        elif id==9:
            self.vendor=self._readstr2uni(ufile,length)
            return
        elif id==10:
            self.cid=self._readint32(ufile)
            return
        elif id==11:
            self.contentLength = self._readint32(ufile)
            return
        elif id==12:
            ufile.read(4)
            return
        elif id==0x81 or id==0x83 or id==0x84:
            self.additionalCheck=self._readuint32(ufile)
            return
        elif id==0x0e:
            ufile.read(1)
            return
        elif id==0x0f:
            ufile.read(1)
            return
        elif id==130:
            ufile.read(1)
            self.additionalCheck=self._readuint32(ufile)
            return
        ufile.read(length)
    
    def _prewrite(self):
        if len(self.title)==0:
            raise UMDException('need umd title')
        if len(self.author)==0:
            raise UMDException('need umd author')
        if len(self.chapters)==0:
            raise UMDException('no chapters')
        for chpt in self.chapters:
            if chpt.content[-1]!=u'\u2029':
                chpt.content=chpt.content+u'\u2029'
        self.zippedSeg=[]
        self.chapOff=[0]*len(self.chapters)
        self.year=str(self.publishDate.year)
        self.month=str(self.publishDate.month)
        self.day=str(self.publishDate.day)
        self.pgkSeed=random.randint(0x401,0x7ffe)%0xffff
        self.cid=random.randint(0x5f5e101,0x3b9aca00-1)
        num1=0
        cttlst=[]
        for i in xrange(len(self.chapters)):
            chpt=self.chapters[i]
            chpt.content=chpt.content.replace(u'\r\n',u'\u2029')
            cttlst.append(chpt.content)
            self.chapOff[i]=num1
            num1+=len(chpt.content)*2
        self.contentLength=num1
        self.text=u''.join(cttlst)
        cttbuflst=[]
        for i in xrange(len(self.chapters)):
            chpt=self.chapters[i]
            cttbuflst.append(chpt.content.encode(self.encoding))
        cttbuf=''.join(cttbuflst)
        if len(cttbuf)%0x8000 ==0:
            num2= len(cttbuf)/0x8000
        else:
            num2=len(cttbuf)/0x8000 +1
        num1=0
        for i in xrange(num2):
            stt=num1
            if 0x8000 < len(cttbuf)-num1:
                ed=num1+0x8000
            else:
                ed=num1+len(cttbuf)-num1
            cdt=zlib.compress(cttbuf[stt:ed])
            self.zippedSeg.append(cdt)
            num1=ed

    def write(self,ufile):
        '''
        ufile: a binary file-like object
        '''
        self._prewrite()
        self._writeuint32(ufile,0xde9a9b89)
        self._writesection(1,0,3,ufile)
        self._writesection(2,0,len(self.title.encode(self.encoding)),ufile)
        self._writesection(3,0,len(self.author.encode(self.encoding)),ufile)
        self._writesection(4,0,len(self.year.encode(self.encoding)),ufile)
        self._writesection(5,0,len(self.month.encode(self.encoding)),ufile)
        self._writesection(6,0,len(self.day.encode(self.encoding)),ufile)
        if len(self.gender)!=0:
            self._writesection(7,0,len(self.gender.encode(self.encoding)),ufile)
        if len(self.publisher)!=0:
            self._writesection(8,0,len(self.publisher.encode(self.encoding)),ufile)
        if len(self.vendor)!=0:
            self._writesection(9,0,len(self.vendor.encode(self.encoding)),ufile)
        self._writesection(11,0,4,ufile)
        self.additionalCheck=0x3000+random.randint(0,0xfff-1)
        self._writesection(0x83,0,4,ufile)
        self._writeadditional(0x83,self.additionalCheck,len(self.chapOff)*4,ufile)
        num1=0
        for chpt in self.chapters:
            num1+=len(chpt.title)*2+1
        self.additionalCheck=0x4000+random.randint(0,0xfff-1)
        self._writesection(0x84,1,4,ufile)
        self._writeadditional(0x84,self.additionalCheck,num1,ufile)
        num2=0
        num3=0
        if len(self.zippedSeg)>1:
            num2=random.randint(0,len(self.zippedSeg)-2)
            num3=random.randint(0,len(self.zippedSeg)-2)
        self.refContent=[0]*len(self.zippedSeg)
        for i in xrange(len(self.zippedSeg)):
            buffer1=self.zippedSeg[i]
            self.refContent[i]=(1<<32)+random.randint(1,0xfffffff-1)*-1
            self._writeadditional(0x84,self.refContent[i],len(buffer1),ufile)
            if i==num2:
                self._writesection(0xf1,0,0x10,ufile)
            if i==num3:
                self._writesection(10,0,4,ufile)
        self.additionalCheck=0x2000+random.randint(0,0xfff-1)
        self._writesection(0x81,1,4,ufile)
        self._writeadditional(0x81,self.additionalCheck,len(self.refContent)*4,ufile)
        if self.cover!=None:
            self.additionalCheck=0x1000+random.randint(0,0xfff-1)
            tmpf=cStringIO.StringIO()
            self.cover.save(tmpf,'gif')
            self._writesection(130,1,5,ufile)
            self._writeadditional(130,self.additionalCheck,len(tmpf.getvalue()),ufile)
        self._writesection(12,1,4,ufile);
        ufile.close()
    

        

    def _writeadditional(self,id,check,length,ufile):
        self._writechar(ufile,'$')
        self._writeuint32(ufile,check)
        self._writeuint32(ufile,length+9)
        if id==0x81:
            numArray1=self.refContent
            num1=0
            while num1 <len(numArray1):
                num2=numArray1[num1]
                self._writeuint32(ufile,num2)
                num1+=1
            return
        elif id==130:
            self._writeimg(ufile,self.cover)
        elif id==0x83:
            numArray2=self.chapOff
            num1=0
            while num1 < len(numArray2):
                num2=numArray2[num1]
                self._writeint32(ufile,num2)
                num1+=1
            return
        elif id==0x84:
            if self.additionalCheck == check:
                for chpt in self.chapters:
                    self._writebyte(ufile,len(chpt.title)*2)
                    self._writeuni2str(ufile,chpt.title)
            else:
                num1=self.refContent.index(check)
                if num1 !=-1:
                    ufile.write(self.zippedSeg[num1])
            return


    def _writesection(self,id,b,length,ufile):
        self._writechar(ufile,'#')
        self._writeint16(ufile,id)
        self._writebyte(ufile,b)
        self._writebyte(ufile,length+5)
        if id==1:
            self._writebyte(ufile,1)
            self._writeint16(ufile,self.pgkSeed)
            return
        elif id==2:
            self._writeuni2str(ufile,self.title)
            return
        elif id==3:
            self._writeuni2str(ufile,self.author)
            return
        elif id==4:
            self._writeuni2str(ufile,self.year)
            return
        elif id==5:
            self._writeuni2str(ufile,self.month)
            return
        elif id==6:
            self._writeuni2str(ufile,self.day)
            return
        elif id==7:
            self._writeuni2str(ufile,self.gender)
            return
        elif id==8:
            self._writeuni2str(ufile,self.publisher)
            return
        elif id==9:
            self._writeuni2str(ufile,self.vendor)
            return
        elif id==10:
            self._writeint32(ufile,self.cid)
            return
        elif id==11:
            self._writeint32(ufile,self.contentLength)
            return
        elif id==12:
            self._writeuint32(ufile,ufile.tell()+4)
            return
        elif id==0x81 or id==0x83 or id==0x84:
            self._writeuint32(ufile,self.additionalCheck)
            return
        elif id==130:
            self._writebyte(ufile,1)
            self._writeuint32(ufile,self.additionalCheck)
            return
        elif id==0xf1:
            ufile.write('\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
            return

class UMDException(Exception):
    pass
