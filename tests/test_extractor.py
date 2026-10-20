import pytest
from app.core.extractor import extract_entities
from app.core.normalizer import normalize_number

def test_normalize_number():
    assert normalize_number("0112-345 678") == "0112345678"
    assert normalize_number("+6012-345-6789") == "0123456789"
    assert normalize_number("1122 3344 5566") == "112233445566"

def test_extract_messy_inputs():
    messy_inputs = [
        # Phones with +60, spaces, and dashes
        ("Call +6010-123 4567 now!", {"phones": ["0101234567"], "accounts": []}),
        ("WhatsApp +60 19-876 5432", {"phones": ["0198765432"], "accounts": []}),
        ("Contact 011 2233 4455", {"phones": ["01122334455"], "accounts": []}),
        
        # Bank accounts with spaces and dashes
        ("Maybank: 1620 1234 5678", {"phones": [], "accounts": ["162012345678"]}),
        ("Transfer to CIMB 701-234-5678", {"phones": [], "accounts": ["7012345678"]}),
        
        # Mixed numbers (Phone vs Bank Account)
        ("Hubungi 012-3456789 atau bayar ke 112233445566", {"phones": ["0123456789"], "accounts": ["112233445566"]}),
        
        # URLs and Shorteners
        ("Click bit.ly/scam-link to claim", {"urls": ["bit.ly/scam-link"]}),
        ("Visit https://lhdn-cukai.apk to pay", {"urls": ["https://lhdn-cukai.apk"]}),
        ("Go to maybank2u-verify.com.my", {"urls": ["maybank2u-verify.com.my"]}),
        
        # Money amounts with and without spaces
        ("Tunggakan cukai RM1,850.50", {"money_amounts": ["RM1,850.50"]}),
        ("Sila bayar RM 2.50 untuk pos laju", {"money_amounts": ["RM 2.50"]}),
        ("Denda sebanyak RM5000 segera", {"money_amounts": ["RM5000"]}),
        
        # Complex multi-entity scam messages
        (
            "Pos Laju: bayar RM2.50 ke 152011122233. Klik s.id/pos",
            {"accounts": ["152011122233"], "money_amounts": ["RM2.50"], "urls": ["s.id/pos"]}
        ),
        (
            "LHDN: Anda ada tunggakan. Call +6011-1234-5678. Bayar ke 7011223344.",
            {"phones": ["01112345678"], "accounts": ["7011223344"], "money_amounts": []}
        ),
        (
            "Kerja sambilan komisen RM100. Hubungi 019 111 2222 atau layari kerja.com",
            {"phones": ["0191112222"], "money_amounts": ["RM100"], "urls": ["kerja.com"]}
        )
    ]
    
    for text, expected in messy_inputs:
        result = extract_entities(text)
        for key, expected_list in expected.items():
            for item in expected_list:
                assert item in result[key], f"Failed to extract {item} from '{text}'"