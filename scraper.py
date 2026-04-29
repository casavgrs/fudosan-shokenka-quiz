#!/usr/bin/env python3
"""
不動産証券化マスター 一問一答データ更新スクリプト
使い方: python3 scraper.py
"""

import requests, json, time, re, os
from bs4 import BeautifulSoup
from datetime import date

NOTE_USER = 'akshay13'
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

SUBJECT_MAP = {
    '102':  {'name': '102 不動産証券化の概要',          'color': '#2563EB'},
    '103':  {'name': '103 不動産の鑑定評価と市場分析',   'color': '#16A34A'},
    '104上':{'name': '104上 不動産証券化の法務',         'color': '#D97706'},
    '104下':{'name': '104下 会計',                       'color': '#7C3AED'},
    '106':  {'name': '106 専門家責任・倫理',              'color': '#0891B2'},
}

# 記事キー → 科目 マッピング（手動設定）
ARTICLE_SUBJECTS = {
    'n58ebb022aa5c': '102',  # 102 重要数字セレクション
    'neb916f6efa34': '102',  # 102 不動産証券化総論
    'nb4e0d9039873': '102',  # 102 不動産の基礎知識
    'n795228e47e16': '102',  # 102 機関投資家
    'n4d3756a78027': '102',  # 101→102 機関投資家
    'n7b556d083404': '102',  # 102 金融市場①
    'nfd5d2d7fd5c3': '102',  # 102 証券市場②
    'nd8046317932f': '102',  # 102 情報開示③
    'ndd4a822bf663': '102',  # 102 利回り計算④
    'nf69c1d136e05': '102',  # 102 銀行業務⑤
    'n56acc674af52': '102',  # 102 プロジェクトファイナンス⑥
    'na74e53fb11d6': '102',  # 102 PFI⑦
    'n8eed269fc451': '102',  # 102 バーゼルⅡ⑧
    'n1f04919a90f4': '103',  # 103 重要数字セレクション
    'n9342588840a9': '103',  # 103 公的な地価
    'n7dc447c816e7': '103',  # 103 アセットタイプ
    'n102294136c3f': '103',  # 103 ER
    'n4ca54201cb7e': '103',  # 103 PM①
    'n833ed025b035': '103',  # 103 PM②
    'nfd9c2e8924c3': '103',  # 103 PM③
    'nb1e96e49d649': '103',  # 103 PM④
    'nf9381c11c703': '103',  # 103 PM⑤
    'nf1dabeeceb7c': '103',  # 103 PM⑥
    'n1f02a32ef5ca': '104下',# 会計⑦
    'nb5d909b25b3f': '104下',# 会計⑧
    'nfa61424a986a': '106',  # 専門家責任
}

SKIP_KEYS = {'n3865609f5aad', 'nc3a3f5cd2f22'}


def fetch_all_articles():
    all_articles, page = [], 1
    while True:
        url = f'https://note.com/api/v2/creators/{NOTE_USER}/contents?kind=note&page={page}'
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()['data']
        all_articles.extend(data['contents'])
        print(f'  ページ {page}: {len(data["contents"])}件（計{len(all_articles)}件）')
        if data['isLastPage']:
            break
        page += 1
        time.sleep(0.5)
    return all_articles


def jp2int(s):
    return int(s.translate(str.maketrans('１２３４５６７８９０', '1234567890')))


def parse_qa(text):
    text = re.sub(r'[ \t]+', ' ', text)
    sections = re.split(r'答え(?:（[^）]*）)?', text)
    all_q, all_a = {}, {}
    offset = 0
    for i in range(0, len(sections) - 1, 2):
        qblock, ablock = sections[i], sections[i + 1]
        pat = r'(?<!\d)([１２３４５６７８９０\d]{1,2})[．.。]\s*(.+?)(?=(?:[１２３４５６７８９０\d]{1,2}[．.。]|\Z))'
        for m in re.finditer(pat, qblock, re.DOTALL):
            try:
                n = jp2int(m.group(1)) + offset
                q = m.group(2).strip()
                if q and len(q) > 3:
                    all_q[n] = q
            except Exception:
                pass
        for m in re.finditer(pat, ablock, re.DOTALL):
            try:
                n = jp2int(m.group(1)) + offset
                all_a[n] = m.group(2).strip()
            except Exception:
                pass
        offset += 50
    result = []
    for n in sorted(all_q):
        q = all_q[n]
        at = all_a.get(n, '')
        ans, exp = 'unknown', ''
        if at:
            f = at[0]
            if f in ('○', 'O', 'Ｏ', '〇'):
                ans, exp = '○', at[1:].strip().lstrip('\u3000 ')
            elif f in ('×', 'X', 'Ｘ'):
                ans, exp = '×', at[1:].strip().lstrip('\u3000 ')
            else:
                ans, exp = 'unknown', at
        result.append({'q': q, 'a': ans, 'exp': exp})
    return result


def fetch_article_text(url):
    time.sleep(1.0)
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    main = soup.find('main') or soup.find('article') or soup.body
    return main.get_text(' ', strip=True) if main else ''


def main():
    print('📡 note記事一覧を取得中...')
    articles = fetch_all_articles()
    print(f'合計 {len(articles)} 件\n')

    subjects_data = {
        k: {'id': k, 'name': v['name'], 'color': v['color'], 'sections': []}
        for k, v in SUBJECT_MAP.items()
    }

    targets = [
        a for a in articles
        if a['canRead'] and a['key'] not in SKIP_KEYS
        and a['key'] in ARTICLE_SUBJECTS
    ]
    print(f'📥 Q&A取得対象: {len(targets)} 記事\n')

    for article in targets:
        key = article['key']
        subj = ARTICLE_SUBJECTS[key]
        title = article['name']
        url = article['noteUrl']
        print(f'  [{subj}] {title[:55]}')
        text = fetch_article_text(url)
        if not text:
            print('    → 取得失敗')
            continue
        qas = parse_qa(text)
        if not qas:
            print('    → Q&A未検出（スキップ）')
            continue
        sc = len(subjects_data[subj]['sections'])
        sid = f"{subj}-{sc + 1:02d}"
        for i, qa in enumerate(qas):
            qa['id'] = f"{sid}-{i + 1:03d}"
        subjects_data[subj]['sections'].append({
            'id': sid, 'title': title, 'note_url': url, 'questions': qas
        })
        print(f'    → {len(qas)} 問取得')

    # 新規記事を追記（既存のdata.jsonにあればスキップ）
    final = {
        'version': '1.0',
        'updated': str(date.today()),
        'subjects': [v for v in subjects_data.values() if v['sections']]
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    total = sum(len(s['questions']) for sub in final['subjects'] for s in sub['sections'])
    print(f'\n✅ 完了: {total} 問 / {len(final["subjects"])} 科目')
    print(f'   保存先: {OUTPUT_FILE}')


if __name__ == '__main__':
    main()
