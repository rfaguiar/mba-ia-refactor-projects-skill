const { AppError } = require('../middlewares/errorHandler');
const { hashPassword, randomPassword } = require('./passwordService');
const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../config/constants');

class CheckoutService {
    constructor({ courseModel, userModel, enrollmentModel }) {
        this.courseModel = courseModel;
        this.userModel = userModel;
        this.enrollmentModel = enrollmentModel;
    }

    async checkout({ name, email, password, courseId, card }) {
        const course = await this.courseModel.findActiveById(courseId);
        if (!course) throw new AppError(404, 'Curso não encontrado');

        const existingUser = await this.userModel.findByEmail(email);
        const userId = existingUser ? existingUser.id : await this.registerUser({ name, email, password });

        const status = card.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        if (status === PAYMENT_STATUS.DENIED) throw new AppError(400, 'Pagamento recusado');

        const enrollmentId = await this.enrollmentModel.enrollWithPayment({
            userId,
            courseId,
            amount: course.price,
            status,
        });
        return { msg: 'Sucesso', enrollment_id: enrollmentId };
    }

    async registerUser({ name, email, password }) {
        const passwordHash = await hashPassword(password || randomPassword());
        return this.userModel.create({ name, email, passwordHash });
    }
}

module.exports = CheckoutService;
