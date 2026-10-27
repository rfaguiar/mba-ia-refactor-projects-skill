const express = require('express');
const adminAuth = require('../middlewares/adminAuth');

function buildRoutes({ checkoutController, adminController, userController }) {
    const router = express.Router();

    router.post('/checkout', checkoutController.checkout);
    router.get('/admin/financial-report', adminAuth, adminController.financialReport);
    router.delete('/users/:id', adminAuth, userController.remove);

    return router;
}

module.exports = buildRoutes;
