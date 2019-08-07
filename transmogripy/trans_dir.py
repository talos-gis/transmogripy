import warnings
from pathlib import Path
from glob import iglob
import os.path

from . import convert, TransmogripyWarning, FatalTransmogripyWarning


def trans_dir(glob_path, dst_root):
    root_path = glob_path[:glob_path.find('*')]
    if os.path.isdir(glob_path):
        glob_path = os.path.join(glob_path, r'**\*.pas')
    display = not glob_path.endswith('*.pas')

    blacklist = []
    files = iglob(glob_path)

    count = {'ok': 0, 'skipped': 0, 'fatal': 0, 'warnings': 0}

    for f in files:
        if f in blacklist:
            print(f'file {f} skipped')
            count['skipped'] += 1
            continue

        try:
            source = Path(f).read_text()
        except Exception:
            print(f)
            raise

        try:
            with warnings.catch_warnings(record=True) as log:
                dest = convert(source)
        except NotImplementedError as e:
            print(f'file {f} not supported ({e})')
            count['fatal'] += 1
        else:
            transmogripy_warnings = []
            for w in map(lambda x: x.message, log):
                if isinstance(w, FatalTransmogripyWarning):
                    display = True
                    transmogripy_warnings.append(w)
                elif isinstance(w, TransmogripyWarning):
                    transmogripy_warnings.append(w)
                else:
                    warnings.warn(w)

            if display:
                print(f)
                print(source)
                print('\n ||\n\\||/\n \\/\n')
                print(dest + '\n\n----------\n')
                for w in transmogripy_warnings:
                    print(w)
                break
            elif transmogripy_warnings:
                count['warnings'] += 1
                print(f)
                for w in transmogripy_warnings:
                    print(f'\t{w}')
            else:
                count['ok'] += 1

            base_name = f[len(root_path):-len('.pas')] + '.py'
            dst_name = os.path.join(dst_root, base_name)
            dst_dir = os.path.dirname(dst_name)
            os.makedirs(dst_dir, exist_ok=True)
            Path(dst_name).write_text(dest)

    print(f'\ntotal: {sum(count.values())} files processed')
    for k, v in sorted(count.items(), key=lambda x: x[1], reverse=True):
        if v == 0:
            break  # since the values are sorted, a zero means all the rest are zero too
        print(f'\t{k}: {v} files')
