const env = process.env;

module.exports = {
    port: Number(env.PORT) || 3000,
    dbFile: env.DB_FILE || ':memory:',
    paymentGatewayKey: env.PAYMENT_GATEWAY_KEY || '',
    adminToken: env.ADMIN_TOKEN || '',
    isProduction: env.NODE_ENV === 'production',
};
