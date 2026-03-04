# test_auth.py
from auth_utils import hash_password, verify_password

# Test 1: Hash a password
plain_password = "MySecret123"
hashed = hash_password(plain_password)
print(f"Original password: {plain_password}")
print(f"Hashed password:   {hashed}")
print(f"Hash length: {len(hashed)} characters\n")

# Test 2: Verify correct password
is_correct = verify_password("MySecret123", hashed)
print(f"✅ Correct password verification: {is_correct}")  # Should be True

# Test 3: Verify wrong password
is_wrong = verify_password("WrongPassword", hashed)
print(f"❌ Wrong password verification: {is_wrong}")  # Should be False

# Test 4: Same password produces different hashes (salt randomization)
hash1 = hash_password("TestPassword")
hash2 = hash_password("TestPassword")
print(f"\n🔐 Same password, different hashes:")
print(f"Hash 1: {hash1}")
print(f"Hash 2: {hash2}")
print(f"Are they different? {hash1 != hash2}")  # Should be True