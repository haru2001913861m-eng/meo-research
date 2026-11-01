"""リスト作り v2（list_build・会長 2026-11-01「リストの質を上げて」）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import list_build as B


def test_site_kind():
    assert B.site_kind("") == "none"
    assert B.site_kind("https://www.instagram.com/shop/") == "sns"
    assert B.site_kind("https://tabelog.com/tokyo/A1/") == "portal"
    assert B.site_kind("https://hamarepo.com/story.php?story_id=123") == "article"
    assert B.site_kind("https://active-future.jp/shop/abc") == "company"
    assert B.site_kind("https://ichie1510.com/") == "own"


def _pages(pages):
    return lambda u: pages.get(u.rstrip("/"), ("", []))


def test_read_site_takes_only_checked_mail_and_form_and_hire():
    pages = {"https://cafe-a.jp": ("カフェA 営業時間 info@cafe-a.jp スタッフ募集中", [("/contact", "お問い合わせ"), ("https://www.instagram.com/cafe_a/", "IG")])}
    s = B.read_site("https://cafe-a.jp/", _pages(pages))
    assert s["email"] == "info@cafe-a.jp"
    assert s["form"].endswith("/contact") and s["hire"] and "cafe_a" in s["instagram"]


def test_read_site_rejects_form_address():
    pages = {"https://cafe-b.jp": ("連絡先 webform@cafe-b.jp", [])}
    s = B.read_site("https://cafe-b.jp/", _pages(pages))
    assert s["email"] == ""


def test_judge():
    card = {"name": "喫茶 ひだまり"}
    assert B.judge(card, {"closed": True}, {}, {})[0] == "閉業"
    assert B.judge(card, {}, {"no_sales": True, "email": "a@b.jp"}, {})[0] == "営業お断り"
    assert B.judge(card, {}, {}, {})[0] == "連絡の道なし"
    assert "返事" in B.judge(card, {}, {"email": "a@b.jp"}, {"rv_n": 10, "rv_replies": 9})[0]
    why, ways = B.judge(card, {}, {"email": "a@b.jp", "form": "https://x/contact"}, {"rv_n": 10, "rv_replies": 1})
    assert why == "" and set(ways) == {"email", "form"}
