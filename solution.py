import os

remap = {}

remap["OM2021_W0"] = "w2450560971"
remap["OM2021_W1"] = "w2450508212"
remap["OM2021_W2"] = "w2450511665"
remap["OM2021_W3"] = "w2450512021"
remap["OM2021_W4"] = "w2450512232"
remap["OM2021_W5"] = "w2450512434"
remap["OM2021_W7"] = "w2450512626"
remap["OM2021_W8"] = "w2450512809"

remap["OM2022_FlakeSalt"] = "w2788066123"
remap["OM2022_LeaveNoTrace"] = "w2788066279"
remap["OM2022_RustRemoval"] = "w2788066771"
remap["OM2022_SoothingSalve"] = "w2788066865"
remap["OM2022_LubricatingSolvents"] = "w2788066950"
remap["OM2022_FilmCrystal"] = "w2788067038"
remap["OM2022_AetherReactor"] = "w2788067624"
remap["OM2022_Fulmination"] = "w2788067677"
remap["OM2022_PotentPainkillers"] = "w2788067760"
remap["OM2022_RadioReceivers"] = "w2788067896"

remap["OM2023_W0_EndGame"] = "w2946682691"
remap["OM2023_W1_SelfPressurizingGas"] = "w2946682999"
remap["OM2023_W2_WasteReclamation"] = "w2946683186"
remap["OM2023_W3_HydroponicSolution"] = "w2946683261"
remap["OM2023_W4_BiosteelFilament"] = "w2946684529"
remap["OM2023_W5_ProbeModule"] = "w2946684660"
remap["OM2023_WO_CoolEarrings"] = "w2946693353"
remap["OM2023_W6_BicrystalTransceiver"] = "w2946687073"
remap["OM2023_W7_WarpFuel"] = "w2946687209"

remap["OM2021Demo_HornSilver"] = "w2513871683"
remap["OM2021Demo_GreenVitriol"] = "w2539581468"
remap["OM2021Demo_FerrousWheel"] = "w2565611826"
remap["OM2021Demo_ArtificialOre"] = "w2591419339"
remap["OM2022Weeklies_MartialRegulus"] = "w2827119474"
remap["OM2022Weeklies_PhilosophersCatalyst"] = "w2868339730"
remap["OM2022Weeklies_NightmareFuel"] = "w2829050875"
remap["OM2022Weeklies_IgnitionCord"] = "w2839120106"
remap["OM2022Weeklies_Cuprite"] = "w2868328394"
remap["OM2022Weeklies_LustrousSyrup"] = "w2868331650"


class Solution():
    def __init__(self, full_path):
        self.folder, self.file_name = os.path.split(full_path)
        self.full_path = full_path

        with open(full_path, "rb") as in_file:
            self.data: bytes = in_file.read()
        self.c = 0
        self.magic_number = self.__read_bytes(4)  # dunno what this is
        self.puzzle_name = self.__read_string()
        self.solution_name = self.__read_string()

        # I'm not super happy rewriting the solution name here
        self.puzzle_name = remap.get(self.puzzle_name, self.puzzle_name)

        self.scores = self.__read_int()

        if self.scores == 4:
            self.__read_int()  # always 0
            self.cycles = self.__read_int()
            self.__read_int()  # always 1
            self.cost = self.__read_int()
            self.__read_int()  # always 2
            self.area = self.__read_int()
            self.__read_int()  # always 3
            self.instructions = self.__read_int()

            self.score_string = f'{self.cost}g/{self.cycles}c/{self.area}a/{self.instructions}i'
        else:
            self.score_string = 'FAILED/UNCOMPLETED'

        self.rest = self.data[self.c:]

    def __read_bytes(self, n):
        out = self.data[self.c:self.c+n]
        self.c += n
        return out

    def __read_number(self, n):
        out = int.from_bytes(self.data[self.c:self.c+n], 'little')
        self.c += n
        return out

    def __read_byte(self):
        return self.__read_number(1)

    def __read_int(self):
        return self.__read_number(4)

    def __read_string(self):
        # todo, this has a problem with unicode characters more than 1 byte wide
        length = self.__read_byte()
        out = self.data[self.c: self.c + length].decode('utf-8')
        self.c += length
        return out

    def __str__(self):
        return f'{self.puzzle_name} {self.file_name[:-9]:4} {self.solution_name:30} {self.score_string}'
        # todo, change this
        # return ' '.join(map(str, parts))
