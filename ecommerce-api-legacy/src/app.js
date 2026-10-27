const express = require('express');
const config = require('./config');
const Database = require('./database/connection');
const { initSchema } = require('./database/schema');
const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const CheckoutService = require('./services/checkoutService');
const ReportService = require('./services/reportService');
const CheckoutController = require('./controllers/checkoutController');
const AdminController = require('./controllers/adminController');
const UserController = require('./controllers/userController');
const buildRoutes = require('./routes');
const { errorHandler } = require('./middlewares/errorHandler');

async function main() {
    const db = new Database(config.dbFile);
    await initSchema(db);

    const userModel = new UserModel(db);
    const courseModel = new CourseModel(db);
    const enrollmentModel = new EnrollmentModel(db);
    const checkoutService = new CheckoutService({ courseModel, userModel, enrollmentModel });
    const reportService = new ReportService({ courseModel });

    const app = express();
    app.use(express.json());
    app.use('/api', buildRoutes({
        checkoutController: new CheckoutController({ checkoutService }),
        adminController: new AdminController({ reportService }),
        userController: new UserController({ userModel }),
    }));
    app.use(errorHandler);

    app.listen(config.port, () => {
        console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

main().catch((err) => {
    console.error('Falha ao iniciar a aplicação:', err);
    process.exit(1);
});
