const crypto = require('crypto');
const config = require('../config');
const { AppError } = require('./errorHandler');

const TOKEN_HEADER = 'x-admin-token';
let warned = false;

function tokenMatches(received, expected) {
    const a = crypto.createHash('sha256').update(received).digest();
    const b = crypto.createHash('sha256').update(expected).digest();
    return crypto.timingSafeEqual(a, b);
}

// Com ADMIN_TOKEN configurado exige o header; sem token só libera fora de produção.
function adminAuth(req, res, next) {
    if (config.adminToken) {
        const received = req.get(TOKEN_HEADER) || '';
        if (!tokenMatches(received, config.adminToken)) return next(new AppError(403, 'Acesso negado'));
        return next();
    }
    if (config.isProduction) return next(new AppError(403, 'Acesso negado'));
    if (!warned) {
        console.warn('[WARN] ADMIN_TOKEN não configurado: rotas administrativas abertas (somente fora de produção).');
        warned = true;
    }
    return next();
}

module.exports = adminAuth;
