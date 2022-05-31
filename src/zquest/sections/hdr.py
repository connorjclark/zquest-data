from ..field import F
from ..version import Version


def get_hdr_field(version: Version, sversion: int) -> F:
    # pre-1.93
    is_old_version = version.preamble == b'AG Zelda Classic Quest File\n '
    if is_old_version:
        return F(type='object', fields={
            'padding': 'B',
            'zelda_version': 'H',
            'internal': 'H',
            'quest_number': 'B',
            'quest_rule_0': 'B',
            'quest_rule_1': 'B',
            'map_count': 'B',
            'old_str_count': 'B',
            'zq_tiles': 'B',
            'midi_flags': F(type='bytes', arr_len=4),
            'cheats_2': 'B',
            'dummy': F(type='bytes', arr_len=14),
            'quest_rule_2': 'B',
            'quest_rule_3': 'B',
            'dummy_2': 'B',
            'version': '9s',
            'title': '65s',
            'author': '65s',
        })

    templatepath_len = 2048
    if sversion == 1:
        templatepath_len = 280

    return F(type='object', fields={
        'zelda_version': 'H',
        'build': 'B',
        'pw_hash': F(type='bytes', arr_len=16) if sversion >= 3 else None,
        'pwd': F(type='bytes', arr_len=30) if sversion < 3 else None,  # oh lordy
        'pwd_key': F(type='H') if sversion < 3 else None,
        'internal': 'H',
        'quest_number': 'B',
        'version': '9s',
        'min_version': '9s',
        'title': '65s',
        'author': '65s',
        'use_keyfile': 'B',
        'flag_tiles': 'B',
        'dummy_1': F(type='bytes', arr_len=4),
        'flag_cheats_2': 'B',
        'dummy_2': F(type='bytes', arr_len=14),
        'template_path': f'{templatepath_len}s',
        'map_count': 'B',

        **({
            'new_version_id_main': 'I',
            'new_version_id_second': 'I',
            'new_version_id_third': 'I',
            'new_version_id_fourth': 'I',
            'new_version_id_alpha': 'I',
            'new_version_id_beta': 'I',
            'new_version_id_gamma': 'I',
            'new_version_id_release': 'I',
            'new_version_id_date_year': 'H',
            'new_version_id_date_month': 'B',
            'new_version_id_date_day': 'B',
            'new_version_id_date_hour': 'B',
            'new_version_id_date_minute': 'B',
            'new_version_devsig': '256s',
            'new_version_compilername': '256s',
            'new_version_compilerversion': '256s',
            'product_name': '1024s',
            'compilerid': 'B',
            'compilerversionnumber_first': 'I',
            'compilerversionnumber_second': 'I',
            'compilerversionnumber_third': 'I',
            'compilerversionnumber_fourth': 'I',
            'developerid': 'H',
            'made_in_module_name': '1024s',
            'build_datestamp': '256s',
            'build_timestamp': '256s',
        } if sversion >= 4 else {}),

        'build_timezone': '6s' if sversion >= 5 else None,
        'external_zinfo': 'B' if sversion >= 6 else None,
        'new_version_is_nightly': 'B' if sversion >= 7 else None,
    })
