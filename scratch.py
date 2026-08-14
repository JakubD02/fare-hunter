from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test 1: proste hasło
result = bcrypt_context.hash("test1234")
print(f"Test 1 OK: {result[:20]}...")

# Test 2: czy podwójny hash się wywali?
first_hash = bcrypt_context.hash("test1234")
print(f"First hash length: {len(first_hash)}")

try:
    second_hash = bcrypt_context.hash(first_hash)
    print(f"Second hash OK: {second_hash[:20]}...")
except ValueError as e:
    print(f"Second hash FAILED: {e}")