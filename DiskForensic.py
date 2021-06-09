# -*- coding: utf-8 -*-
"""
Created on Fri May 28 15:16:10 2021

@author: >//<
          c
"""

###  import library  ###
import sys
import hashlib
import os
import bitstring as bs
###  import library  ###

#fungsi 1: menangani informasi entri dari partisi
def part_entry_info(partentry):
    entry_info_raw = partentry
    #catatan: BitArray dapat membaca: offset, panjang = value * 8 (bit per byte)
    #"old"parttype = bs.BitArray(bytes=partentry,offset=32,length=8)#offset = 04 * 8
    #membaca dari bitarray: partentry[start:end:step], ingat untuk * 8
    while int(str(partentry), 16) !=0x00:
        ###  tipe partisi  ###
        print(" Tipe Partisi:",type_of_partition(partentry))
        ###  memulai sector  ###
        print(" Memulai Sektor:",starting_sector(partentry))
        ###  ukuran partisi  ###
        print(" Ukuran dari Sektor:",size_of_partition(partentry))
        ###  akhir dari informasi entri   ###
        break
    else:
        print(" Partisi Tidak Tersedia.\n")
        
#fungsi 2: menampilkan type_of_partition
def type_of_partition(partentry): # top = type_of_partition
    parttype = partentry[32:40:] #position 04h , 4*8=32,size=1, (4+1)*8=40
    t = int(str(parttype), 16)
    if t == 0x00:
        return("Tidak Diketahui Atau Kosong")
    elif t == 0x01:
        return("12-bit FAT")
    elif t == 0x04:
        return("16-bit FAT")
    elif t == 0x05:
        return("Ext MS-DOS")
    elif t == 0x06:
        return("FAT 16")
    elif t == 0x07:
        return("NTFS")
    elif t == 0x0B:
        return("FAT 32(CHS)")
    elif t == 0x0C:
        return("FAT 32(LBA)")
    elif t == 0x0E:
        return("FAT 16(LBA)")
    else:
        return("Terjadi Kesalahan Dalam Membaca Tipe dari Partisi")

#fungsi 3: menghitung jumlah partisi (sesuai perulangan)
def number_of_partition(MBR): #akan mengambil informasi jumlah partisi dalam raw(disk)
    # entry_info_raw = bs.BitArray(bytes=partentry)
    #partition entry
    # value = int(str(partentry))
    # entri partisi mendapat referensi/learned dari MBR
    entries = bs.BitArray(bytes=MBR,offset=446*8,length=16*8*4)
    n = 0 #titik awal menghitung partisi
    entrieslist = []
    for entry in entries.cut(16*8): #16 byte per entry, 8 bit per byte.
        entrieslist.append(entry)
    for entry in entrieslist:
        if int(str(entry), 16) !=0:
            n += 1
    return(n) # mengatasi masalah diperbaiki dengan pendekatan/approach baru ini.

    #for i in range(1,4):
    #    if int(str(entries[:16*8*i:16*8]),16) != ' ':
    #        n +1= 1
    # return(n)

#fungsi 4: Memulai Pengukuran partisi (sector)
def starting_sector(partentry):
    start_sec_raw = partentry[8*8:12*8:]
    start_sec = []
    #conversi little-endian ke big-endian
    for byte in start_sec_raw.cut(8):
        start_sec.append(byte)
    start_sec = start_sec[::-1]
    start_sec = start_sec[0] + start_sec[1] + start_sec[2] + start_sec[3]
    return(int(str(start_sec),16))

#fungsi 5: size_of_partition atau ukuran dari partisi
def  size_of_partition(partentry):
    #ukuran sector = 512 bytes
    size_info_raw = partentry[12*8::]
    size_info = []
    #conversi little-endian ke big-endian
    for byte in size_info_raw.cut(8):
        size_info.append(byte)
    size_info = size_info[::-1]
    size_info = size_info[0] + size_info[1] + size_info[2] + size_info[3]
    return(int(str(size_info),16))

#fungsi 6: Menampilkan Informasi Volume FAT
#catatan: fungsi ini hanya mendefinisikan partisi Tipe FAT-16
def fat_volume(partentry):
    #pengambilan nilai partentry dan menentukan untuk memulai sector
    fat_start_sec_raw = partentry[8*8:12*8:]
    fat_start_sec= []
    #konversi little-endian ke big-endian
    for byte in fat_start_sec_raw.cut(8):
        fat_start_sec.append(byte)
    fat_start_sec = fat_start_sec[::-1]
    fat_start_sec = fat_start_sec[0] + fat_start_sec[1] + fat_start_sec[2] + fat_start_sec[3]
    fat_start_sec = int(str(fat_start_sec),16)
    print("Memulai sektor FAT dalam decimal: ",fat_start_sec)
    ##########Membaca data mentah/raw pada sektor awal FAT
    #mengambil data antara MBR dan sektor sebanyak 63 kali
    #ambil lagi jumlah 62 * 512 byte untuk mencapai sektor volume pertama
    #jadi "junk" akan menjadi (fat start sector)-1 
    # serta 1 ini menunjukkan MBR di sektor
    junk = f.read((fat_start_sec-1)*512) #titik posisi: sector 63
    #print(len(junk))
    
    #berikutnya 512 bytes akan menjadi sektor pertama dalam volume
    #membaca di data dalam volume FAT pada sektor pertama
    first_sector_of_volume = f.read(512) #titik posisi: sector 64
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ number  sektor per cluster
    
    #print("first_sector_of_volume raw data:")
    #print(first_sector_of_volume)
    
    # nomer sektor per cluster
    # offset 0Dh = 13, 13 * 8, length 1 byte, 1*8
    num_of_secpclus = bs.BitArray(bytes=first_sector_of_volume,offset=13*8,length=1*8)
    print("Nomor sector per cluster: ",int(str(num_of_secpclus),16))
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ukuran dari FAT area
    # Size of the FAT area = size of FAT in sectors * number of FAT copies
    # ukuran FAT dalam sectors offset 16h,size 2, number of FAT copies/menyalin offset 10h,size 1
    size_of_per_fat_raw = bs.BitArray(bytes=first_sector_of_volume,offset=22*8,length=2*8)
    
    # konversi little-endian ke big-endian
    size_of_per_fat = []
    for byte in size_of_per_fat_raw.cut(8):
        size_of_per_fat.append(byte)
    size_of_per_fat = size_of_per_fat[::-1]
    size_of_per_fat = size_of_per_fat[0]+size_of_per_fat[1]
    
    # print(size_of_per_fat)
    # nomor salinan hanya satu byte, tidak perlu untuk convert endian.
    num_of_fat_copies = bs.BitArray(bytes=first_sector_of_volume,offset=16*8,length=1*8)
    #print(num_of_fat_copies)
    size_of_fat_area = int(str(size_of_per_fat),16) * int(str(num_of_fat_copies),16)
    print("Ukuran area FAT dalam sektor:",size_of_fat_area)
     
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ size of the root directory
    # size of root dir = max num of root dir entries * dir entry size in byte / sector size
    # maksimal num dari root dir entri dengan offset 11h, ukuran 2 bytes. 11h = 17d
    # ukuran dir dari  FAT adalah 32 bytes.
    # sector size = 512 bytes.
    dir_entry_size = 32
    sector_size = 512
    max_num_of_dir_raw = bs.BitArray(bytes=first_sector_of_volume,offset=17*8,length=2*8)
    
    # konversi little-endian ke big-endian
    max_num_of_dir = []
    for byte in max_num_of_dir_raw.cut(8):
        max_num_of_dir.append(byte)
    max_num_of_dir = max_num_of_dir[::-1]
    max_num_of_dir = max_num_of_dir[0]+max_num_of_dir[1]
    max_num_of_dir = int(str(max_num_of_dir),16)
    
    # print(max_num_of_dir)
    # size of the root dir
    size_of_root_dir = int(max_num_of_dir * dir_entry_size / sector_size)
    print("Ukuran dari Root Directory dalam sektor:",size_of_root_dir)
    
    ###############alamat klasifikasi sektor ke dua
    # sec_addr_of_clus_2 = first sector of data area + root dir size
    # first sec of data = first sec of volume + reserved area size + size of fat area
    # size of reserved area offset 0Eh = 14d
    # size of reserved area:
    size_of_reserved_raw = bs.BitArray(bytes=first_sector_of_volume,offset=14*8,length=2*8)
    #konversi little-endian ke big-endian 
    size_of_reserved = []
    for byte in size_of_reserved_raw.cut(8):
        size_of_reserved.append(byte)
    size_of_reserved = size_of_reserved[::-1]
    size_of_reserved = size_of_reserved[0]+size_of_reserved[1]
    size_of_reserved = int(str(size_of_reserved),16)
    print("Ukuran yang dipesan: ",size_of_reserved)
    
    #detik pertama volume dan ukuran area "FAT" dihitung sebelumnya
    first_sec_of_data_area = int(str(fat_start_sec),16) + size_of_reserved + size_of_fat_area
    print("Sektor pertama dari area data: ",irst_sec_of_data_area)
    
    #alamat klasifikasi sector yang ke dua
    sec_addr_of_clus_2 = first_sec_of_data_area + size_of_root_dir
    print("klasifikasi sector nomor dua:")
    
    #8 sector per cluster/klasifikasi
    print("     Sektor",sec_addr_of_clus_2,"to sector",sec_addr_of_clus_2 + 8,"\n")
    
    ##########################Tentang Penghapusan File:
    print("--------------------------------")
    print("Tentang file pertama yang dihapus pada direktori root: ")
    print("--------------------------------")
    
    # singkirkan data yang tidak perlu dari gambar disk, yaitu terus membaca hingga direktori root
    # dari atas, f.read() mencapai sektor pertama volume FAT.
    # keluarkan sisa area yang dipesan:
    reserved_rest = f.read((size_of_reserved-1)*512) #  possisi: sector 65
    
    #take out the FAT area of this volume, 502 sectors, 512 bytes per sectors
    fat_area_raw_data = f.read(size_of_fat_area*512) # posisi: sector 567
    
    # baca di direktori root: size = 32 sector * 512 byte.
    root_dir_raw_data = f.read(size_of_root_dir*512) # posisi: sector 599
    
    # uji apakah data yang benar terbaca.
    #print(root_dir_raw_data)# diuji
    #ubah data raw  ke bit array:
    files_raw = bs.BitArray(bytes=root_dir_raw_data)
    
    # pisahkan entri file dalam direktori root ke dalam array
    file_entries =[]
    for entry in files_raw.cut(32*8): #32 bytes per entri
       file_entries.append(entry)
       
    # print(file_entries) # diuji, benar.
    # menentukan apakah entri adalah file yang sudah ada
    exiting_files = []
    for entry in file_entries:
        file_head = entry[:32:]
        if int(str(file_head),16) != 0:
            exiting_files.append(entry)
    
    # menentukan apakah file tersebut dihapus dan mengambil file yang dihapus ke array baru
    deleted_files= []
    for entry in exiting_files:
        file_head = entry[8]
        #print(file_head) # diuji, benar.
        
        if int(str(file_head),16) == 0xe5:
            deleted_files.append(entry)
            
    #print(deleted_files) # diuji.
    
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ mengerjakan file pertama yang dihapus:
    while len(deleted_files) != 0:
        deleted_file=deleted_files[0]
        
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ nama file
        deleted_file_name = deleted_file[:11*8:]
        #deleted_file_name = codecs.decode("deleted_file_name","hex")
        del_filename_char = []
        for byte in deleted_file_name.cut(8):
            byte = chr(int(str(byte),16))
        print("Nama file yang Dihapus Pertama: ",''.join(del_filename_char))
        
        # ukuran offset file: 0x1C hingga 0x1F
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ukuran file
        deleted_files_size_raw = deleted_file[28*8:32*8:]
        
        #konversi little-endian ke big-endian
        del_file_size = []
        for byte in deleted_files_size_raw.cut(8):
            del_file_size.append(byte)
        del_file_size = del_file_size[::-1]
        del_file_size = del_file_size[0]+del_file_size[1]+del_file_size[2]+del_file_size[3]
        
        #print(del_file_size) #diuji.
        
        print("Ukuran file yang dihapus dalam byte: ", int(str(del_file_size),16))
        
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ nomor cluster pertama dari file:
        #offset addr cluster pertama: 0x1A to 0x1B
        first_cluster_num_raw = deleted_file[26*8:28*8:]
        
        #konversi little-endian ke big-endian
        first_cluster_num = []
        for byte in first_cluster_num_raw.cut(8):
            first_cluster_num.append(byte)
        first_cluster_num = first_cluster_num[::-1]
        first_cluster_num = first_cluster_num[0]+ first_cluster_num[1]
        first_cluster_num = int(str(first_cluster_num),16)
        print("Nomor cluster pertama dari file yang dihapus: ", first_cluster_num)
        
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@ "pergi" ke cluster pertama dari file yang dihapus
        raw_data_on_cluster_2_17 = f.read((first_cluster_num-2)*8*512)
        
        # posisi file saat ini: sektor 735
        first_cluster_of_delfile_raw = f.read(8*512)
        
        #ubah data ke bitarray.
        first_cluster_of_delfile = bs.BitArray(bytes=first_cluster_of_delfile_raw)
        #print(first_cluster_of_delfile_raw) # uji.
        
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 16 karakter pertama file
        first_cluster_of_del_file = []
        for byte in first_cluster_of_delfile.cut(8):
             byte = chr(int(str(byte),16))
             first_cluster_of_del_file.append(byte)
        first_16_character = first_cluster_of_del_file[0:16]
        
        #CATATAN: baris di bawah ini mencetak 16 karakter RAW pertama
        #print("16 karakter pertama sebelum memformat: ", first_16_character)
        print("16 karakter pertama dari file yang dihapus: ", end='')
        print(''.join(first_16_character))
        break
    
    else:
        print("    Maaf, Tidak ada file terhapus yang ditemukan di partisi ini.")
        # CATATAN: ini mencetak "Bagian A" setelah melewatkan satu baris, ini karena
        # karakter awal menyertakan beberapa perintah pemformatan. yaitu \n
        ############################################################# # Akhir info volume FAT.
        
#fungsi 7: informasi tentang volume NTFS.
def ntfs_info(ntfs_entry):
    start_sec_ntfs = starting_sector(ntfs_entry)
    # "pergi" ke volume ntfs:
    # CATATAN: awal image file  sudah dibaca.
    # first 63 sectors + reserved of FAT + FAT area + root dir + (19-2) clusters
    # + first cluster of the del file
    # thus 1(MBR)+62(rest)+1(FAT_firstsec)+1(reservedrest)+502(fatarea)+32(rootdir)
    # +17*8(clus_not_mentioned)+1*8(first_clus_of_del_file) = 743 sectors.
    # jadi (starting sector 1606500) - (used 743 sectors of the file )
    # akan membawa file ke sektor awal NTFS.
    print("Tunggu beberapa saat, sedang membaca info pada NTFS...")
    
    junk_ntfs = f.read((start_sec_ntfs-743)*512) #posisi saat ini: sektor 1606500
    # CATATAN: metode di atas akan membutuhkan sedikit lebih banyak waktu untuk diproses, tidak dapat menemukan
    # cara yang lebih baik untuk membaca file.
    # baris di atas harus mengambil file untuk mengimbangi 3106c800h
    
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ sektor pertama NTFS
    first_sector_of_ntfs = f.read(512) #posisi saat ini: sektor 1606501
    # diuji jika benar info sudah terbaca.
    
    #print(first_sector_of_ntfs) # bisa diuji.
    
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ bytes per sector:
    # bytes per sector offset 0Bh, size 2 byte.
    ntfs_byte_per_sec = bs.BitArray(bytes=first_sector_of_ntfs,offset=11*8,length=2*8)
    #print(ntfs_byte_per_sec) #bisa diuji.
    
    #konversi little-endian ke big-endian
    ntfsbyte_per_sector = []
    for byte in ntfs_byte_per_sec.cut(8):
        ntfsbyte_per_sector.append(byte)
    ntfsbyte_per_sector = ntfsbyte_per_sector[::-1]
    ntfsbyte_per_sector = ntfsbyte_per_sector[0]+ntfsbyte_per_sector[1]
    print("NTFS Bytes per sector: ", int(str(ntfsbyte_per_sector),16))
    
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ sector per cluster:
    # sectors per cluster offset 0x0D, ukuran 1 byte.
    ntfs_sec_per_clus = bs.BitArray(bytes=first_sector_of_ntfs,offset=13*8,length=1*8)
    
    # 1 byte, tidak perlu mengonversi endian.
    ntfs_sectorPcluster = int(str(ntfs_sec_per_clus),16)
    print("NTFS sektor per cluster: ",ntfs_sectorPcluster)
    
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ alamat sektor untuk file $MFT
    #$MFT alamat cluster offset 0x30, ingat untuk mengalikan dengan 8 sektor.
    MFT_cluster_addr = bs.BitArray(bytes=first_sector_of_ntfs,offset=48*8,length=8*8)
    #print(MFT_cluster_addr) #uji
    
    #konversi little-endian ke big-endian
    Mca = [] # Mca seperti pada "alamat cluster MFT"
    for byte in MFT_cluster_addr.cut(8):
        Mca.append(byte)
    Mca = Mca[::-1]
    #print(Mca) #pengujian
    
    Mca= Mca[0]+Mca[1]+Mca[2]+Mca[3]+Mca[4]+Mca[5]+Mca[6]+Mca[7]
    Mca = int(str(Mca),16)
    
    # Mca adalah alamat cluster, alamat sektor = sektor pertama NTFS + Mca
    Msa = Mca * 8 + start_sec_ntfs
    print("Alamat sektor dari file $MFT: ",Msa)
    
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ jenis dan panjang dua atribut pertama
    # CATATAN: jenis atribut offset 0-3d, panjang 4byte
    # CATATAN: panjang atribut offset 4-7d, panjang 4byte.
    # membaca data $MFT:
    #4 cluster * 8 sec_per_clus =32, sudah membaca 1 sektor pertama, jadi 31*512.
    to_mft_junk = f.read((Mca*8-1)*512) #posisi: sector 1606532
    mft_file_raw = f.read(2*512) #posisi: sector 1606533
    #print(mft_file_raw) #Silahkan uji.
    
    #offset ke atribut pertama: 20-21d, 0x14-0x15
    ######## offset lokasi atribut pertama
    first_attrib = bs.BitArray(bytes=mft_file_raw,offset=20*8,length=2*8)
    
    #konversi little-endian ke big-endian
    first_attribute = []
    for byte in first_attrib.cut(8):
        first_attribute.append(byte)
    first_attribute = first_attribute[::-1]
    first_attribute = first_attribute[0]+first_attribute[1]
    first_attribute = int(str(first_attribute),16)
    #print(first_attribute) #nilai 56d, 0x38, diuji.
    
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ atribut_type_identifier pertama
    attribute_type_id = bs.BitArray(bytes=mft_file_raw,offset=first_attribute*8,length=4*8)
    
    #konversi little-endian ke big-endian
    attrTpID = []
    for byte in attribute_type_id.cut(8):
        attrTpID.append(byte)
    attrTpID = attrTpID[::-1]
    attrTpID = attrTpID[0]+attrTpID[1]+attrTpID[2]+attrTpID[3]
    attrTpID = int(str(attrTpID),16)
    print("\nTipe dari atribut pertama: ", attribute_type_text(attrTpID))
    
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ panjang atribut pertama
    attrib_length_raw = bs.BitArray(bytes=mft_file_raw,offset=(first_attribute+4)*8,length=4*8)
     
    #konversi little-endian ke big-endian
    attrlen = []
    for byte in attrib_length_raw.cut(8):
         attrlen.append(byte)
    attrlen = attrlen[::-1]
    attrlen = attrlen[0]+attrlen[1]+attrlen[2]+attrlen[3]
    attrlen = int(str(attrlen),16)
    print("Panjang atribut pertama: ",attrlen)
    
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ tipe atribut kedua
    # offset atribut kedua = offset 1 + panjang 1.
    offset_of_2nd = first_attribute + attrlen
    attr2_raw = bs.BitArray(bytes=mft_file_raw,offset=offset_of_2nd*8,length=4*8)
    
    #konversi little-endian ke big-endian
    attr2_type = []
    for byte in attr2_raw.cut(8):
        attr2_type.append(byte)
    attr2_type = attr2_type[::-1]
    attr2_type = attr2_type[0]+attr2_type[1]+attr2_type[2]+attr2_type[3]
    #print(attr2_type) #uji
    attr2_type = int(str(attr2_type),16)
    
    print("\nTipe Atribut Ke-dua: ",attribute_type_text(attr2_type))
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ panjang atribut ke dua
    attr2_len_raw = bs.BitArray(bytes=mft_file_raw,offset=(offset_of_2nd+4)*8,length=4*8)
    
    #konversi little-endian ke big-endian
    attr2_len = []
    for byte in attr2_len_raw.cut(8):
        attr2_len.append(byte)
    attr2_len = attr2_len[::-1]
    attr2_len = attr2_len[0]+attr2_len[1]+attr2_len[2]+attr2_len[3]
    attr2_len = int(str(attr2_len),16)
    print("Panjang atribut ke-dua: ",attr2_len)

#fungsi 7.1 Identifikasi atribute NTFS
def attribute_type_text(attrTpID):
    if attrTpID == 16:
        return("$STANDART_INFORMATION")
    elif attrTpID == 32:
        return("$ATTRIBUTE_LIST")
    elif attrTpID == 48:
        return("$FILE_NAME")
    elif attrTpID == 64:
        return("$OBJECT_ID")
    elif attrTpID == 80:
        return("$SECURITY_DESCRIPTOR")
    elif attrTpID == 96:
        return("$VOLUME_NAME")
    elif attrTpID == 122:
        return("$VOLUME_INFORMATION")
    elif attrTpID == 128:
        return("$DATA")
    elif attrTpID == 144:
        return("$INDEX_ROOT")
    elif attrTpID == 160:
        return("$INDEX_ALLOCATION")
    elif attrTpID == 176:
        return("$BITMAP")
    elif attrTpID == 192:
        return("$REPARSE_POINT")
    elif attrTpID == 256:
        return("$LOGGED_UTILITY_STREAM")
    else:
        return("Terjadi kesalahan dalam membaca tipe atribut")
    
    
#################################fungsi hash file
   
def getFileHashValue(fname):
	BLOCKSIZE = 65536	# good when we are dealing with big files.
	md5HashObj = hashlib.md5()
	with open(fname, 'rb') as binFileHandler:
		buf = binFileHandler.read(BLOCKSIZE)
		while len(buf) > 0:
			md5HashObj.update(buf)
			buf = binFileHandler.read(BLOCKSIZE)
	return md5HashObj.hexdigest()

# To either use the program from CMD or from a Python IDE
if len(sys.argv) < 2:
	os.chdir('./')
else:
	os.chdir(sys.argv[1])
	
dictFnameHashVal = {}
notUniq = 0

for f in os.listdir():
	if os.path.isfile(f):
		hashValue = getFileHashValue(f)
		if hashValue not in dictFnameHashVal.values():
			dictFnameHashVal[f] = hashValue
		else:
			notUniq += 1




############################## biarkan alat mengambil parameter file gambar disk
#penggunaan: python3 DiskForensix.py Sample_1.dd
dd = sys.argv[0]
# CATATAN: fungsi parameter ini belum selesai, perlu kerja lebih lanjut

############################################################# ######### Coba membaca file .dd
with open(dd,'rb') as f:
    #test membaca file
    #Saran: tambahkan titik poin lainnya: if file name == *.dd, kemudian lanjut ke
    if f.read(1)  != "":
    #CATATAN: tidak dapat menggunakan f.read() untuk pengujian karena membaca (mengkonsumsi) 1 byte dari
    #file, menyebabkan seluruh pembacaan file kacau.
        print("\nDisk image <%s> Berhasil Dibaca!\n" % dd )
    else:
       print("\nError loading <%s>...\n" % dd)
    
    ############################################################Membaca file ke dalam variabel string
    #MBR:
    MBR = f.read(512) # Posisi: sector 1
    firstpartentry = bs.BitArray(bytes=MBR,offset=446*8,length=16*8)
    secondpartentry = bs.BitArray(bytes=MBR,offset=(446+1*16)*8,length=16*8)
    thirdpartentry = bs.BitArray(bytes=MBR,offset=(446+2*16)*8,length=16*8)
    fourthpartentry = bs.BitArray(bytes=MBR,offset=(446+3*16)*8,length=16*8)
    bootrecordsignature = bs.BitArray(bytes=MBR,offset=(446+4*16)*8,length=2*8)
    
    ############################################################# ########### sapa pengguna
    print("Halo, Anda menggunakan gambar disk %s" % dd)
    print("********************************")
    print("Informasi Dasar")
    print("********************************")
    ####################################################### Number of partitions
    print("Nomor Dari Partisi:",number_of_partition(MBR))
    ################################################ first partition information
    print("\nPartisi pertama:",part_entry_info(firstpartentry))
    ############################################### Second partition information
    print("\nPartisi kedua:",part_entry_info(secondpartentry))
    ################################################ Third partition information
    print("\nPartisi ketiga:",part_entry_info(thirdpartentry))
    ############################################### Fourth partition information
    print("\nPartisi keempat:",part_entry_info(fourthpartentry))
    
    
    ################################################################## Detail dari partisi FAT 16
    # mendefinisikan entri FAT dan entri NTFS
    all_entries = [firstpartentry,secondpartentry,thirdpartentry,fourthpartentry]
    fat_entry = ''
    ntfs_entry = ''
    for entry in all_entries:
        if int(str(entry[32:40:]),16) == 0x06:
            fat_entry = entry
        elif int(str(entry[32:40:]),16) == 0x07:
            ntfs_entry = entry
    
    print("********************************")
    print("Specific Information of the FAT partition:")
    print("********************************")
    
    while fat_entry != '':
        fat_volume(fat_entry)
        break
    else:
        print("  Maaf, Tidak ada informasi berguna yang ditemukan")
    
    ############################################################# Detail volume NTFS
    print("********************************")
    print("Informasi Spesifik dari partisi NTFS: ")
    print("********************************")
    
    while ntfs_entry != '':
        ntfs_info(ntfs_entry)
        break
    else: 
        print("  Maaf, Tidak ada informasi berguna yang ditemukan")
        
        
############################hash file output dari fungsi hash
# Write the results to file
with open('Hasil.txt', 'w') as resFile:
	resFile.write("{0:50} {1}\n".format("File Name","Hash Value"))
	resFile.write("#" * 90 + "\n")
	# Check if the hash value is UNIQUE or not before writing
	for fName in dictFnameHashVal:
		if fName not in ['results.txt','hashcalc.py']:	# Don't want those in the results file
			resFile.write("{0:50} {1}\n".format(fName,dictFnameHashVal[fName]))	

#print(dictFnameHashVal)
print("Jumlah file non-unik adalah {0}".format(notUniq))

        
f.close()
# CATATAN: ubah nilai ascii ke metode nilai hex: hex = format(ord("ascii"),"x")
# CATATAN: format default fungsi print() adalah pergi ke baris berikutnya setelah print
# print("some text", end=' ') akan menempatkan baris ini dan cetakan berikutnya pada baris yang sama.
