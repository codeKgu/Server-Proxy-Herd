import datetime

FLOOD = "FLOOD"
WHATSAT = "WHATSAT"
IAMAT = "IAMAT"
NONE = "NONE"


class ParseMessage:

    def __init__(self, message):
        self._message = message
        self._message_split = message.split()
        self.message_type = NONE

    def check_command(self):
        if len(self._message_split) < 4:
            return self.message_type
        command = self._message_split[0]
        if command == FLOOD:
            self.message_type = FLOOD
            self.time = float(self._message_split[4])
            self.id = self._message_split[2]
            self.get_long_lat(self._message_split[3])
        else:
            if len(self._message_split) != 4:
                return self.message_type
            if command == WHATSAT:
                self.message_type = WHATSAT
            elif command == IAMAT:
                self.message_type = IAMAT
            else:
                pass
        return self.message_type

    def get_long_lat(self, message):
        count = 0
        latitude, longitude = [], []
        for char in message:
            if char == '+' or char == '-':
                count += 1
            if count == 1:
                latitude.append(char)
            elif count == 2:
                longitude.append(char)
            else:
                return False
        self.lat = "".join(latitude)
        self.long = "".join(longitude)
        return latitude, longitude

    def check_iso_standard(self):
        iso_message = self._message_split[2]
        latitude, longitude = self.get_long_lat(iso_message)
        lat_temp = "".join(latitude[1:]).split('.')
        long_temp = "".join(longitude[1:]).split('.')
        if len(lat_temp[0]) not in [2, 4, 6] or len(long_temp[0]) not in[3, 5, 7] or len(lat_temp) != 2 or len(long_temp) != 2:
            return False
        for lat, long in zip(lat_temp, long_temp):
            if not lat.isdigit() or not long.isdigit():
                return False
        if int(lat_temp[0]) > 90 or int(long_temp[0]) > 180:
            return False
        return True

    def check_posix(self):
        try:
            time = float(self._message_split[3])
            datetime.datetime.utcfromtimestamp(time)
        except (ValueError, OSError) as e:
            return False
        time = self._message_split[3].split('.')
        if len(time[1]) > 9:
            return False
        return True

    def check_iamat(self):
        if not self.check_iso_standard() or not self.check_posix():
            return False
        self.id = self._message_split[1]
        self.loc = self._message_split[2]
        self.time = float(self._message_split[3])
        return True

    def check_whatsat(self):
        if int(self._message_split[2]) < 0 or int(self._message_split[2]) > 50:
            return False
        elif int(self._message_split[3]) <= 0 or int(self._message_split[3]) > 20:
            return False
        else:
            self.id = self._message_split[1]
            self.radius = int(self._message_split[2])
            self.num_results = int(self._message_split[3])
            return True
