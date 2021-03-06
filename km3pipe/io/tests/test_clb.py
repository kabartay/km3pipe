# coding=utf-8
# Filename: test_clb.py
# pylint: disable=C0111,R0904,C0103
"""
...

"""
from __future__ import division, absolute_import, print_function

from km3pipe.testing import TestCase, StringIO
from km3pipe.io.clb import CLBPump, CLBHeader, PMTData

import binascii

__author__ = "Tamas Gal"
__copyright__ = "Copyright 2016, Tamas Gal and the KM3NeT collaboration."
__credits__ = []
__license__ = "MIT"
__maintainer__ = "Tamas Gal"
__email__ = "tgal@km3net.de"
__status__ = "Development"


HEX_DATA = ("7A0500005454444300000000000000030000684200BEBC2030BEAF008000000" +
            "00003F2F79B0C0003F64C6B060F03F7560B1C0F03F75631030203F88BEB040A" +
            "04039B750B0404059CF2050404059F7E0C040405AC880B1404083F480A0A040" +
            "98CEA060B04099B1A020A040A4E1E090A040AC7FA070A040B199E0B00040C92" +
            "B20600040CDB170A05040F92840E04041063550A140410770A16000410EE911" +
            "B00041336E605040413870707000413F20E100504142BA21204041495151000" +
            "0415D2311C14041828A9041404182C491702041C73D40600041E68902108041" +
            "EFBD40F0004222E3405140425CD0F051404274D3C050A0428E54F0A050429EC" +
            "0D0300042BEF780500042BF0F10600042BF23A0B00042BF24B0400042BF4D90" +
            "300042BF9150300042C0ABB0E00042C2018061B042CA6BF0307042CF8ED0C0B" +
            "042CF89B160B042CFB0F060B042D279A0D0C042D29F6080B042D7A2B1000042" +
            "DB7271005043070E602140431A40A02140431B4A404140431B61609050431C5" +
            "2F0A140431E4CA090004324D4A260A04327A26041404327DB907020433B73D0" +
            "91104340D2D041104341626080004356B551700043597A6091A04362222171A" +
            "04362F16050004368FCF3000043A4CD41900043E7BE50300044017300B00044" +
            "026AD0E0404403C950F04044047EE0B0404404B41130804425F5607000442F4" +
            "0A0D040442FC6B0E0504463FB80E0C0446890D031A044875DA15000448FB210" +
            "D0B044B94310605044B95010905044EFF220F05044EFF350300044F7ED20300" +
            "044FEB3104050450722D0D1404533BD407050453B31E0C00045443541600045" +
            "4BE120905045643291005045855860205045857BE1A00045C929E0208045CB0" +
            "3F0208045D17F9070804608DE20B050464AF48071404651A3A0B0C0469FE410" +
            "30C0469FE64050C0469FFCE0F18046CC9671D19046CC966330A046CC9660E04" +
            "046EBDBC0F08046FACCA04000470D04511000470DEDA02050472373F0A00047" +
            "3C94904050476AE6108050476B086030B0476B6EB0A070478C35B08140478DE" +
            "1B0314047901AA0314047A6E5C0900047AFFA51100047C47F40608047CD88D0" +
            "B000481AE1F0A140483C96822020484205A0700048554F10314048965870500" +
            "049156F2081B04933F2017000494171D0D1A049573731900049DCB3B1E10049" +
            "EDEB00E14049F197F0305049FC648040C04A372AE021404A42B03050504AABF" +
            "771F0804AB6FD80D1204AD3BAF031604AED0DB060A04B42C8E0A0504B589131" +
            "B1404B5D55C051A04B816A5080004B87A7E020504B87A77100A04B8C4010500" +
            "04BA01C3250004BA0DC3060004BA0DD2020404BA9FB6110004BDFB4D070004B" +
            "DFE42030504C41C020C0004C715920A0804C73EAF080504C7434F0F0004C75E" +
            "540B0004C8A3B7070504C92DD5090204CCC690050404CD1395060504CD68170" +
            "90404CF1CBC061A04CF42A5060004D0BF720D0004D2CC07061404D3462C2214" +
            "04D3476C091404D349A40A0804D37D890A0104D503CD041404D5CB6A020404D" +
            "65C5C060104D8FD0F040B04DA69E10A0004DB16C5060804DCBFAD040804DD75" +
            "DA040804DD7F15080404DD8187050704DE2D8E090B04E0BB43090004E16DDE2" +
            "10004E3DA35140B04E48E2E0D0504E4F796100F04E5691F110004E8D5B8060A" +
            "04EA7027040A04EA752F0D0A04EA99A5081404EAEFBF0A1404ECC77F0A0004E" +
            "F3F37040A04F110BF080004F309DC080004F47A91030504F5C254100404FA0D" +
            "4C050104FA1061040C04FDD6E50B0004FDD687240004FDE4D4080C04FDFD2A0" +
            "51A04FEE042090004FF8936180405028A0C07000505EA0604000509845A0D05" +
            "050AB6D9030B05131DAA020B0513B9F51F000516583C0F0A051A25440D02051" +
            "F2A3A031B0521757909070524607C06000525B5C50408052663DF0900052872" +
            "DC0F00052879AC1A02052F56FB08000533D98E076A030000545444430000000" +
            "0000000040000684200BEBC2030BEAF00800000001A0536A45C071B05387A03" +
            "030B053AE0CA10000540B704081405424BAA0F1A0542B64C04050543DCB70E0" +
            "505456028091905477559071405495B3505050549EE790E00054B1FA2030905" +
            "51F12D1D07055314DA050005541EBA0605055487540D050556EE1F060B055AB" +
            "EEF0505055AF4BB0805055B632E0505056044260D07056194BD090C05622F3E" +
            "031E0563F5D8040B05656B810E1405695D650B080569BD4E04140569F1EE1C1" +
            "80569F1EF0C1A0569F1EE171B0569F1F2051C0569F1E67C1C0569F2BD041C05" +
            "69F3AB041D0569F1F6031E0569F1EA32080569F1F00F1B0569F3D1091E056A0" +
            "BDB0205056A8FD6080C056B84D1031C056BFB2B0216056C5D99051C056CF8A3" +
            "081E056CF8A01514056D23190514056FE6830914057367C11E14057367E6041" +
            "4057377EA1F00057438B3070505771BA40A000578372823000578FC4D031405" +
            "7A769D0A0C057D0BEF0500057D7D85080B058160E30900058188BC0A140582C" +
            "6C004080583704A0704058685B711020589A5430F00058A4B390404058D669F" +
            "0A0505921D5F04050595D2B613000596F6A5030A059C2FB7050B059CA512240" +
            "B059CAF96091A059DD2BA1800059E8ABB1207059FCD310707059FD1A1080705" +
            "9FEB620707059FF321050005A017E20E0405A0834A110405A085CA0A0405A09" +
            "04D040405A091E9100405A09354060405A096B6030405A0A8AB080B05A10F44" +
            "0D0005A52952110805A5A2250C0505A6C7EA060B05A770DF191405AA29870C1" +
            "A05AC34D6030205ACC85D130405B23E57240505B4CE421A0005B5CEBE0A1405" +
            "B5D1B4111405B5D43F2E0105B6EB83010005B8CF330A0205BF41B7071A05C0C" +
            "949040A05C15776071705C20CAD031B05C30B4C110805C38A91030405C560EC" +
            "0E0805C56B0F070205C7480D050005C7520B070005C99D613B0005CAA853170" +
            "505CBB43B0A0005D4EB3F1C0005D634EE040C05D718D7030005DB70BE041A05" +
            "DDC0D5090405DE4216091105DF876B080705DFB2D20A1405E15D240E0005E21" +
            "B9F061405E28B87040005E2C98B0B1405E4F888201405E50398050405E545E5" +
            "090405E546410D0405E54874070405E5B1840A0005E8F88A080405E8F7A9110" +
            "505E93B72021A05E95A90060A05E99D01080405EB0E42050A05EC7371040005" +
            "EFD856030505F12515030505F1251C0B7A05000054544443000000000000000" +
            "000006842011E1A3030BEAF00800000001B0002496D0E0B0002BC5C0E000005" +
            "79CF05040006CB4C1207000856D4050C0008748903050010EEAF0B000017E4F" +
            "B0C04001A2E020514001A34860614001D2356070A001E4FED030A001E80CF0E" +
            "14001F32271E140023CC8405000024BECB070A0024FF582F130025924A05150" +
            "025923F41180025924B03090025923B590A002592421C150025961E0E090025" +
            "9EF3190A0025DA660211002765B70607002911D20D00002A09B2050B002A2CE" +
            "70A0A002A724E0A0B002CCF7D0914002D562D060A0030F2C008000031416125" +
            "1A003340B3040400334C093D0400334C78050400334CDE080600334C0875080" +
            "0334C0F110A00334C0F1A0A00334DE1041700334C15091B00334C1809040033" +
            "4D5E060400334F64040600334DDA0804003351BC1104003351D414040033532" +
            "B07060033526E0C0A0033525818040033558906040033559D0E040033563A0F" +
            "04003356A11006003358BA1408003359DA04040033602304040033615E05040" +
            "0336AD10704003371F50504003377F213040033B7B005040033BDC010040033" +
            "FE540A0400340FD40B040034571E10000034D5C516000034E2A9040B00376F4" +
            "313100037FBF11E11003960271705003CF5130F1A004014AB0F00004022C606" +
            "00004026E0081E0041ECCA110A0043D5440A070046372204140046C70D13080" +
            "0479FE40D080047B41405080047C2BB07080048EC820500004AA3670400004C" +
            "57E408050050FDC01305005100C806040052E2B807040052E46106040052E63" +
            "A02040052E8BE07040053155209040053318E0F00005579C02A05005632DF0A" +
            "04005670BE0D140056ADE109140056ADF007140056ADFE02040057A9C3061A0" +
            "05B0BF60510005D00E50400005FE3BF06000061D61D040500623C5B10040062" +
            "628210140062841305050063961907000065072609000067160611140067BD6" +
            "E0610006C87CB0907006E3E41100A007018A70C000078CFB11D0A007B73DD14" +
            "08007D815404000080719407140081AC6F05000081EB54040B008516300F000" +
            "086C3170E00008996150308008D38690614009210EF0407009228F70D0A0092" +
            "767B060A0092A57E04050093F742040A00949AEA11140097F8BA1907009BA68" +
            "C0704009EE8FC0A0B009F9C380B14009FBD39050000A4107A0F0000A6508609" +
            "0000A67C05060000A67C810B0000A68F6E050000A6AD42100000A823350C140" +
            "0AB0AF3110800AFF54C0D0400B109AD0B0500B255D4101A00B52C9E0A0400B8" +
            "8C91030000B8D6FB0C1B00B8E9F52F0000B95CB3230000B96188100500B9CF6" +
            "F0B0000BA3B5D060800BF35920A0800BF433B0E1400C054FA040700C84AE00E" +
            "0700C8548B080A00C89C2E040B00CAB786100800CC0029200800CC035F040A0" +
            "0CCE4290A0500D0695D030500D0BA3E0D1400D24405050000D305BE020000DA" +
            "286C260000DADF13200A00DB1A220F0000DBA8E10C1400DC4A27070500DC6C2" +
            "8190500DC7327140C00DF18BB040000E033CB100100E284B7070100E2BA0D06" +
            "0100E32855150900E39B30050500E4F108081B00E91C37040000EF05C306000" +
            "0F2A102020000F2A3B01A1A00F48B6A060000F6510D040000F7D602021A00F8" +
            "A772021400F8E7AA04000100CB3E1014010405070514010408900D14010408A" +
            "1121A0107419608000107C14F050B010A09650C05010B81880500010B8E4813" +
            "00010BA9D90900010DE4021105010F27AD0B00011206F60D0001125E4E050B0" +
            "1134D9806010115E8550400011A26EF0F00011AA8A80A00011B25E90507011B" +
            "5F6A0B07011B626E1107011B63D1090A011B634C0707011B83E70B07011B8DF" +
            "21205011D9C5E0B1B012140DD15000122E1A105000122F104060001234ED404" +
            "000124B66406140125ABD610070127CBA40A14012DA81B1D1A012DA82206000" +
            "12F7E5F24")


BINARY_DATA = binascii.unhexlify(HEX_DATA.encode())
try:
    TEST_FILE = StringIO(BINARY_DATA)
except TypeError:
    from io import BytesIO
    TEST_FILE = BytesIO(BINARY_DATA)
#    TEST_FILE = StringIO(str(BINARY_DATA))


class TestCLBPump(TestCase):

    def setUp(self):
        TEST_FILE.seek(0, 0)
        self.pump = CLBPump()
        self.pump.blob_file = TEST_FILE

    def test_determine_packet_positions_finds_packets(self):
        self.pump.determine_packet_positions()
        self.assertListEqual([0, 1406, 2284], self.pump.packet_positions)

    def test_seek_to_packet(self):
        pump = self.pump
        pump.determine_packet_positions()
        pump.seek_to_packet(2)
        self.assertEqual(2284, pump.blob_file.tell())
        pump.seek_to_packet(1)
        self.assertEqual(1406, pump.blob_file.tell())

    def test_get_blob(self):
        self.pump.determine_packet_positions()
        blob = self.pump.get_blob(0)
        self.assertEqual(0, blob['CLBHeader'].run_number)
        self.assertEqual('TTDC', blob['CLBHeader'].data_type)
        self.assertEqual(229, len(blob['PMTData']))
        a_pmt_data = blob['PMTData'][0]
        self.assertEqual(0, a_pmt_data.channel_id)
        self.assertEqual(66254747, a_pmt_data.timestamp)
        self.assertEqual(12, a_pmt_data.tot)

    def test_next_blob(self):
        self.pump.determine_packet_positions()
        blob = self.pump.next_blob()
        self.assertEqual(229, len(blob['PMTData']))
        blob = self.pump.next_blob()
        self.assertEqual(141, len(blob['PMTData']))
        blob = self.pump.next_blob()
        self.assertEqual(229, len(blob['PMTData']))

    def test_next_blob_raises_stop_iteration_on_eof(self):
        self.pump.determine_packet_positions()
        self.pump.next_blob()
        self.pump.next_blob()
        self.pump.next_blob()
        self.assertRaises(StopIteration, self.pump.next_blob)


class TestCLBHeader(TestCase):

    def test_init_with_byte_data(self):
        raw_data = "5454444300000000000000030000684200BEBC2030BEAF0080000000"
        byte_data = binascii.unhexlify(raw_data.encode())
        header = CLBHeader(byte_data=byte_data)
        self.assertEqual('TTDC', header.data_type)
        self.assertEqual(0, header.run_number)
        self.assertEqual(3, header.udp_sequence)
        self.assertEqual(26690, header.timestamp)
        self.assertEqual('30beaf00', header.dom_id)
        self.assertEqual('10000000000000000000000000000000', header.dom_status)

    def test_str_representation(self):
        raw_data = "5454444300000000000000030000684200BEBC2030BEAF0080000000"
        byte_data = binascii.unhexlify(raw_data.encode())
        header = CLBHeader(byte_data=byte_data)
        description = "CLBHeader\n" \
                      "    Data type:    TTDC\n" \
                      "    Run number:   0\n" \
                      "    UDP sequence: 3\n" \
                      "    Time stamp:   26690\n" \
                      "                  1970-01-01 07:24:50\n" \
                      "    Ticks [16ns]: 12500000\n" \
                      "    DOM ID:       30beaf00\n" \
                      "    DOM status:   10000000000000000000000000000000\n"
        self.assertEqual(description, str(header))


class TestPMTData(TestCase):

    def test_init(self):
        pmt_data = PMTData(1, 2, 3)
        self.assertEqual(1, pmt_data.channel_id)
        self.assertEqual(2, pmt_data.timestamp)
        self.assertEqual(3, pmt_data.tot)
