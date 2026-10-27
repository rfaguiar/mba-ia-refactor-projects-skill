const crypto = require('crypto');

const PREFIX = 'scrypt';
const KEY_LENGTH = 64;
const SALT_BYTES = 16;

function scrypt(password, salt) {
    return new Promise((resolve, reject) => {
        crypto.scrypt(password, salt, KEY_LENGTH, (err, key) => (err ? reject(err) : resolve(key)));
    });
}

async function hashPassword(password) {
    const salt = crypto.randomBytes(SALT_BYTES).toString('hex');
    const key = await scrypt(password, salt);
    return `${PREFIX}$${salt}$${key.toString('hex')}`;
}

// Aceita o formato novo e valores legados (texto puro) criados pela versão original.
async function verifyPassword(password, stored) {
    if (!stored.startsWith(`${PREFIX}$`)) return stored === password;
    const [, salt, hash] = stored.split('$');
    const key = await scrypt(password, salt);
    const expected = Buffer.from(hash, 'hex');
    return key.length === expected.length && crypto.timingSafeEqual(key, expected);
}

function randomPassword() {
    return crypto.randomBytes(18).toString('base64url');
}

module.exports = { hashPassword, verifyPassword, randomPassword };
