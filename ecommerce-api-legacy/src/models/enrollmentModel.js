class EnrollmentModel {
    constructor(db) {
        this.db = db;
    }

    // Matrícula, pagamento e auditoria são gravados atomicamente.
    enrollWithPayment({ userId, courseId, amount, status }) {
        return this.db.transaction(async () => {
            const { lastID: enrollmentId } = await this.db.run(
                'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
                [userId, courseId]
            );
            await this.db.run(
                'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
                [enrollmentId, amount, status]
            );
            await this.db.run(
                "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
                [`Checkout curso ${courseId} por ${userId}`]
            );
            return enrollmentId;
        });
    }
}

module.exports = EnrollmentModel;
