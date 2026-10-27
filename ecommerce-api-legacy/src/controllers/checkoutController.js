const { AppError } = require('../middlewares/errorHandler');

class CheckoutController {
    constructor({ checkoutService }) {
        this.checkoutService = checkoutService;
        this.checkout = this.checkout.bind(this);
    }

    async checkout(req, res, next) {
        try {
            const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body || {};
            if (!name || !email || !courseId || !card || typeof card !== 'string') {
                throw new AppError(400, 'Bad Request');
            }
            const result = await this.checkoutService.checkout({ name, email, password, courseId, card });
            res.status(200).json(result);
        } catch (err) {
            next(err);
        }
    }
}

module.exports = CheckoutController;
