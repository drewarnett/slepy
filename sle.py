#!/usr/bin/env python3

"""sle.py
"""

import argparse
import os

from pyparsing import (
    alphas,
    common,
    nums,
    one_of,
    rest_of_line,
    srange,
    Combine,
    Char,
    Group,
    Keyword,
    LineEnd,
    Opt,
    ParserElement,
    Suppress,
    Word
    )


def Parser():
    """returns slepy pyparsing statement parser"""

    ParserElement.set_default_whitespace_chars(' \t')

    def statement(expression):
        """statements do not span lines"""

        return expression + Suppress(rest_of_line) + Suppress(LineEnd())

    # not . to avoid matching on frequency
    p_call = (Word(alphas + nums + '/') + ~Char('.')).set_name('callsign')
    p_call.set_parse_action(lambda t:  t[0].upper())

    p_readability = Word(srange('[1-5]'), exact=1)
    p_strength = Word(srange('[1-9]'), exact=1)
    p_tone = Word(srange('[1-9]'), exact=1)
    p_rs = Combine(p_readability + p_strength).set_name('RS')
    p_rst = Combine(p_readability + p_strength + p_tone).set_name('RST')
    p_report = (p_rs ^ p_rst).set_name('RS(T)')
    p_reports = Combine(p_report + ' ' + p_report).set_name('reports')

    p_association = Word(alphas + nums, min=1, max=3).set_name(
        'SOTA summit association')
    p_region = Word(alphas, min=2, max=2).set_name('SOTA summit region')
    p_summit_number = Word(nums, min=1, max=4).set_name('SOTA summit number')
    p_reference = Combine(
            p_association + '/' + p_region + '-' + p_summit_number
        ).set_name('SOTA reference')
    p_reference.set_parse_action(common.upcase_tokens)

    p_s2s_reference = Suppress(Keyword('s2s')) + p_reference
    p_s2s_reference.set_parse_action(lambda t:  t[0])

    p_frequency = common.sci_real.copy().set_results_name('frequency')
    p_frequency.set_name('frequency (has decimal point)')

    p_mode = one_of(
            'cw ssb fm am',
            caseless=True, as_keyword=True
        ).set_results_name('mode')
    p_mode.set_name('mode')
    p_mode.set_parse_action(common.upcase_tokens)

    p_timevalue = Word(nums, min=1, max=4).set_name('timevalue')

    p_zulu = Combine(p_timevalue + 'z').set_name('zulu time')
    p_local = Combine(p_timevalue + 'l').set_name('local time')
    p_am = Combine(p_timevalue + 'a').set_name('AM time')
    p_pm = Combine(p_timevalue + 'p').set_name('PM time')

    p_timestamp = (p_zulu ^ p_local ^ p_am ^ p_pm).set_name('timestamp')

    p_my_call_statement = statement(
            Suppress(Keyword('my_call')) + p_call.set_results_name('my_call'))
    p_my_call_statement.set_name('my call statement')

    p_my_reference_statement = statement(
        Suppress(Keyword('my_reference'))
        + p_reference.set_results_name('my_reference'))
    p_my_reference_statement.set_name('my reference statement')

    p_date_statement = statement(
            common.iso8601_date.copy().set_results_name('date'))
    p_date_statement.set_name('date statement (YYYY-MM-DD)')

    p_timezone_statement = statement(Combine(
            Suppress(Keyword('utc'))
            + common.signed_integer.set_results_name('tz')))
    p_timezone_statement.set_name('timezone statement')

    p_preamble = (
        Opt(p_my_call_statement)
        & Opt(p_date_statement)
        & Opt(p_my_reference_statement)
        & Opt(p_timezone_statement)
        ).set_name('preamble')

    p_frequency_mode = (
        (
            p_frequency.set_results_name('frequency')
            + p_mode.set_results_name('mode'))
        | (
            p_mode.set_results_name('mode')
            + p_frequency.set_results_name('frequency'))
        | p_frequency.set_results_name('frequency')
        | p_mode.set_results_name('mode'))

    p_frequency_mode_statement = statement(
            p_frequency_mode
        ).set_name('frequency and/or mode statement')
    p_frequency_mode.set_parse_action(lambda t:  ('frequency_mode', t))

    p_comments = (Suppress('# ') + rest_of_line).set_name('comments')
    p_comments.set_parse_action(lambda t:  t[0])

    p_qso_statement = statement(
            p_call.set_results_name('their_call')
            + (
                Opt(p_reports.set_results_name('reports'))
                & Opt(p_timestamp.set_results_name('timestamp'))
                & Opt(p_frequency.set_results_name('frequency'))
                & Opt(p_mode.set_results_name('mode'))
                & Opt(p_s2s_reference.set_results_name('reference'))
            ) + Opt(p_comments.set_results_name('comments'))
        )
    p_qso_statement.set_name('QSO statement')
    p_qso_statement.set_parse_action(lambda t:  ('qso', t))

    p_body_statement = p_frequency_mode_statement | p_qso_statement
    p_body_statement.set_name('body statement')

    p_body = p_body_statement[0, ...].set_name('body')

    p_sle = (
        Group(p_preamble).set_results_name('preamble')
        + Group(p_body).set_results_name('body')).set_name('sle')

    return p_sle


def process_intermediate(data):
    """process intermediate data

    data['preamble']:  as dict

        keys/values:
            'my_call':  callsign (str)
            'my_reference':  reference (str)
            'date':  date (str)
            'tz':  tz_offset (str)

    data['body']:  iterable where each may be one of:

        ('frequency_mode', as_dict)

            'frequency':  frequency (str)
            'mode':  mode (str)

            Note:  one or the other or both.

        ('qso', as_dict)

            'their_call':  callsign (str)

            the following are all optional:

                'reports':  'RS(T) RS(T)' (str)
                'timestamp':  'NNNNq' (str)

                    NNNN is 1 to 4 decimal digits

                    q is 'z', 'l', 'a', or 'p'

                'frequency':  frequency (str)
                'mode':  mode (str)
                'reference'  reference (str)
                'comments':  comments (str)

        return value:  list of lists of qso data, my_call, my_reference, date
    """

    my_call = data['preamble']['my_call']
    my_reference = data['preamble']['my_reference']
    date = data['preamble']['date']
    assert my_call
    assert my_reference
    assert date
    timezone_offset = None
    if 'tz' in data['preamble']:
        timezone_offset = data['preamble']['tz']

    table = []

    frequency = None
    mode = None

    for kind, values in data['body']:

        def _use(info, tag, alternate_value):
            rval = alternate_value
            if tag in info and info[tag]:
                rval = info[tag]
            return rval

        assert kind in ('frequency_mode', 'qso'), kind

        if kind == 'frequency_mode':
            frequency = _use(values, 'frequency', frequency)
            mode = _use(values, 'mode', mode)
        elif kind == 'qso':
            their_call = values['their_call']
            reports = _use(values, 'reports', '--- ---')
            their_report, my_report = reports.split(' ')
            timestamp = _use(values, 'timestamp', None)
            frequency = _use(values, 'frequency', frequency)
            mode = _use(values, 'mode', mode)
            their_reference = _use(values, 'reference', None)
            comments = _use(values, 'comments', None)
            table.append([
                their_call, mode, timestamp, frequency, their_reference,
                their_report, my_report, comments])

    return table, my_call, my_reference, date, timezone_offset


def _split_time(hhmm):
    h = hhmm//100
    m = hhmm % 100
    return h, m


def _join_time(h, m):
    rval = h*100 + m
    return rval


def _minutes(h, m):
    return h*60 + m


def _h_m(minutes):
    return minutes//60, minutes % 60


def _timestamp_to_zulu(timestamp, tz_offset=None):
    offset = None
    if tz_offset:
        offset = float(offset)

    kind = timestamp[-1]
    value = int(timestamp[:-1])

    assert kind in 'zlap'

    if kind in 'lap':
        assert timezone_offset, (
            'Timezone offset missing for local time')

    rval = None
    if kind == 'z':
        rval = str(value)
    elif kind == 'l':
        t_h, t_m = _split_time(value)
        t_h -= timezone_offset
        t = _join_time(t_h, t_m)
        rval = str(t)
    elif kind == 'a':
        t_h, t_m = _split_time(value)
        t_h -= timezone_offset
        t = _join_time(t_h, t_m)
        rval = str(t)
    elif kind == 'p':
        t_h, t_m = _split_time(value)
        t_h += 12
        t_h -= timezone_offset
        t = _join_time(t_h, t_m)
        rval = str(t)
    return rval


def patch_time(log_data, timezone_offset=None):
    """time patching pass

    log_data:  list of lists where each has:
               (there_call, mode, timestamp, frequency, their_reference,
                their_report, my_report, comments)

    return value:   timestamp patched up copy of log_data
    """

    rval = log_data[:]
    timestamps = []
    for entry in log_data:
        (
            _their_call, _mode, timestamp, _frequency, _their_reference,
            _their_report, _my_report, _comments
        ) = entry
        if timestamp:
            timestamp = _timestamp_to_zulu(timestamp)
        timestamps.append(timestamp)
    assert timestamps[0] is not None
    assert timestamps[-1] is not None
    while None in timestamps:
        p1 = timestamps.index(None) - 1
        for p2 in range(p1 + 2, len(log_data)):
            if timestamps[p2] is not None:
                break

        h1, m1 = _split_time(int(timestamps[p1]))
        h2, m2 = _split_time(int(timestamps[p2]))
        interval = _minutes(h2, m2) - _minutes(h1, m1)
        step = interval / (p2 - p1)
        for p in range(p1 + 1, p2):
            m = _minutes(h1, m1) + round(step*(p - p1))
            timestamps[p] = str(_join_time(*_h_m(m)))
    for i, t in enumerate(timestamps):
        rval[i][2] = t
    return rval


def log(log_data, my_reference, date):
    """create logbook .txt file content

    log_data:

    my_reference:  (str)

    date:  YYYY-MM-DD (str)

    output:  list of line str
    """

    year, month, day = date.split('-')

    rval = []
    rval.append(f'SOTA activation on {my_reference}')
    for entry in log_data:
        (
            their_call, mode, timestamp, frequency, their_reference,
            their_report, my_report, comments
        ) = entry
        items = [
                f'{year}-{month}-{day}', timestamp, their_call,
                their_report if their_report else '---',
                my_report if my_report else '---',
                frequency, mode]
        if their_reference:
            items.append(f'S2S {their_reference}')
        if comments:
            items.append(comments)
        rval.append(' '.join(str(x) for x in items))
    rval.append('end of activation')
    return rval


def sotalog(log_data, my_call, my_reference, date):
    """write SOTA .csv file"""

    rval = []
    for entry in log_data:
        (
            their_call, mode, timestamp, frequency, their_reference,
            _their_report, _my_report, _comments
        ) = entry
        year, month, day = date.split('-')
        rval.append(','.join(
            str(x) for x in (
                'V2',
                my_call, my_reference,
                f'{day}/{month}/{year}', timestamp,
                str(frequency) + 'MHz', mode,
                their_call,
                '' if their_reference is None else their_reference)))
    return rval


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='simple fast log entry clone for SOTA')

    arg_parser.add_argument(
        '--verbose',
        action='store_true',
        help='enable verbose debugging output')

    arg_parser.add_argument(
        'input_file',
        type=str,
        nargs='?',
        default='',
        help=(
            'sle input file name\n'
            'If not provided, writes slepy_railroad.html.'))

    arg_parser.add_argument(
        '-o',
        type=str,
        default='',
        help=(
            'output directory name (current working directory used if not'
            ' given'))

    args = arg_parser.parse_args()

    ifn = None
    if args.input_file:
        ifn = args.input_file

    output_directory_name = os.getcwd()
    if args.o:
        output_directory_name = args.o

    output_filename_base = None
    if ifn:
        output_filename_base = os.path.splitext(os.path.basename(ifn))[0]

    sfn, lfn = None, None
    if ifn:
        sfn = os.path.join(
            output_directory_name, output_filename_base + '.csv')
        lfn = os.path.join(
            output_directory_name, output_filename_base + '.txt')
    rfn = os.path.join(output_directory_name, 'slepy_railroad.html')

    parser = Parser()

    if not ifn:
        parser.create_diagram(rfn)
    else:
        with open(ifn, encoding='utf8') as ifh:
            parse_tree = parser.parse_file(ifn)
            (
                log_data, my_call, my_reference, date, timezone_offset
            ) = process_intermediate(parse_tree)
            if args.verbose:
                print('preamble:')
                print(parse_tree['preamble'])
                print('body')
                for each in parse_tree['body']:
                    print(each)
            log_data = patch_time(log_data, timezone_offset)
            with open(sfn, 'w', encoding='utf8') as sfh:
                for each in sotalog(log_data, my_call, my_reference, date):
                    sfh.writelines(each + '\n')
            with open(lfn, 'w', encoding='utf8') as lfh:
                for each in log(log_data, my_reference, date):
                    lfh.writelines(each + '\n')
