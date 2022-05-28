class Version:
    def __init__(self, zelda_version=None, build=None, preamble=None):
        self.zelda_version = zelda_version
        self.build = build
        # Not part of any comparisons.
        self.preamble = preamble

    def __str__(self):
        parts = []
        if self.zelda_version != None:
            parts.append(f'zelda_version = {hex(self.zelda_version)}')
        if self.build != None:
            parts.append(f'build = {self.build}')
        return ', '.join(parts)

    def _cmp(self, other):
        if self.zelda_version == None or other.zelda_version == None:
            if self.zelda_version != None or other.zelda_version != None:
                raise 'Invalid input'

        if self.zelda_version > other.zelda_version:
            return 1
        elif self.zelda_version < other.zelda_version:
            return -1

        if self.build == None or other.build == None:
            if self.build != None or other.build != None:
                # TODO: eh, this is wrong and will break eventually.
                raise 'Invalid input'

        if self.build > other.build:
            return 1
        elif self.build < other.build:
            return -1

        return 0

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __lt__(self, other):
        return self._cmp(other) < 0
