# NAW text control by SemD
import json
from os import path
from time import ctime


class NAWFilesControl:
    text_path = './text.json'
    version_file = './version.txt'
    story_file = './story.json'
    patch_file = './patch.txt'
    main_version = 1
    under_version = 5
    editor = 'SemD'

    @staticmethod
    def get_all_nodes(file_type):
        with open(file_type, 'r', encoding='utf-8') as nodes_db:
            data = json.load(nodes_db)
        return data

    @classmethod
    def get_node(cls, key, nodes_type='text'):
        all_nodes = cls.get_all_nodes(cls.text_path if nodes_type == 'text' else cls.story_file)
        try:
            return all_nodes[str(key)]
        except KeyError:
            return ''

    @classmethod
    def check_version(cls):
        cls.check_files()
        for file in [cls.text_path, cls.story_file]:
            last_modf = ctime(path.getmtime(file))[8:].split(' ')
            if last_modf[0] == '':
                last_modf.pop(0)
            last_modf.extend(last_modf[1].split(':'))
            last_modf.pop(1)
            last_modf = list(map(lambda val: int(val), last_modf))
            last_ver_time = cls.get_node("Last modification date", 'text' if file == cls.text_path else 'story')[
                            8:].split(' ')
            if last_ver_time[0] == '':
                last_ver_time.pop(0)
            last_ver_time.extend(last_ver_time[1].split(':'))
            last_ver_time.pop(1)
            last_ver_time = list(map(lambda val: int(val), last_ver_time))
            for i in range(0, 5):
                if last_modf[i] != last_ver_time[i]:
                    cls.set_ver_time(file)
                    return

    @classmethod
    def set_ver_time(cls, file):
        new_time = ctime(path.getmtime(file))
        for data_file in [cls.text_path, cls.story_file]:
            data = cls.get_all_nodes(data_file)
            data['Last modification date'] = new_time
            new_ver = int(data['Version'].split('.')[2])
            new_ver += 1
            new_ver = str(cls.main_version) + '.' + str(cls.under_version) + '.' + str(new_ver)
            data['Version'] = new_ver
            with open(data_file, 'w', encoding='utf-8') as nodes_db:
                json.dump(data, nodes_db, ensure_ascii=False)
        with open(cls.version_file, 'w', encoding='utf-8') as version_file:
            version_file.write(
                "Last modification date:" + new_time + '\n' + 'Version:' + new_ver + '\n' + 'Edit by ' + cls.editor)

    @classmethod
    def check_files(cls):
        for path_file in [cls.text_path, cls.story_file]:
            if not path.exists(path_file):
                with open(path_file, 'w', encoding='utf-8') as nodes_db:
                    json.dump({
                        'Last modification date': ctime(path.getmtime(cls.text_path)),
                        'Version': '0.0.0',
                        'Editor': cls.editor,
                    }, nodes_db, ensure_ascii=False)
        if not path.exists(cls.version_file):
            with open(cls.version_file, 'w', encoding='utf-8') as version_file:
                version_file.write("Last modification date:" + ctime(
                    path.getmtime(cls.text_path)) + '\n' + 'Version:0.0.0\n' + 'Edit by ' + cls.editor)

    @classmethod
    def get_patch(cls):
        with open(cls.version_file, 'r', encoding='utf-8') as version_file:
            version = version_file.readlines()
        with open(cls.patch_file, 'r', encoding='utf-8') as patch_file:
            patch = patch_file.readlines()
        if patch:
            return 'Version\n\n' +''.join(version) + '\n\nPatchnotes\n\n'+''.join(patch)
        else:
            return 'Version\n\n' +''.join(version)
