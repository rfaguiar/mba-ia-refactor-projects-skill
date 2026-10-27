class AppError extends Error {
    constructor(status, message) {
        super(message);
        this.status = status;
    }
}

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    if (err instanceof AppError) return res.status(err.status).send(err.message);
    console.error('[ERROR]', err);
    return res.status(500).send('Erro interno');
}

module.exports = { AppError, errorHandler };
