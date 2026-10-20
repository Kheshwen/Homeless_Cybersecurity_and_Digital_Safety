from app.core.pipelines.url_check import check_urls, get_host


def test_get_host():
    assert get_host("https://www.Maybank2u.com.my/login") == "maybank2u.com.my"
    assert get_host("bit.ly/abc") == "bit.ly"


def test_official_site_is_clean():
    assert check_urls(["https://www.maybank2u.com.my/home"])[0] == 0
    assert check_urls(["https://www.hasil.gov.my"])[0] == 0


def test_apk_is_danger():
    assert check_urls(["http://lhdn-cukai.apk"])[0] >= 90


def test_embedded_official_domain_is_not_trusted():
    assert check_urls(["https://maybank2u.com.my.evil.com/login"])[0] >= 80
    assert check_urls(["evil.com/maybank2u.com.my"])[0] >= 80


def test_lookalike_and_brand_spoof():
    assert check_urls(["maybank2u-verify.com"])[0] >= 80
    assert check_urls(["rnaybank2u.com.my"])[0] >= 80


def test_shortener_is_caution_and_no_false_match():
    assert check_urls(["bit.ly/scam"])[0] == 25
    assert check_urls(["https://www.microsoft.com"])[0] == 0
