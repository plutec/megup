from core import crypto


class TestCrypto():
    def test_encrypt_and_decrypt_AES_CBC_success(self):
        data = '1234567890abcdefghijklmnopqrstuv'
        key = '1234567890abcdef'
        encrypted_data = crypto.aes_cbc_encrypt(data, key)
        decrypted_data = crypto.aes_cbc_decrypt(encrypted_data, key)
        assert decrypted_data == data, (
            'Encrypting and decrypting "%s" with key "%s" did not work.'
            'Instead, got "%s"'  % (data, key, str(decrypted_data)))
