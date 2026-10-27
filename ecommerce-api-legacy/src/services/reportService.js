const { PAYMENT_STATUS } = require('../config/constants');

class ReportService {
    constructor({ courseModel }) {
        this.courseModel = courseModel;
    }

    async financialReport() {
        const rows = await this.courseModel.findAllWithEnrollments();
        const byCourse = new Map();

        for (const row of rows) {
            if (!byCourse.has(row.course_id)) {
                byCourse.set(row.course_id, { course: row.title, revenue: 0, students: [] });
            }
            if (row.enrollment_id === null) continue;

            const entry = byCourse.get(row.course_id);
            if (row.status === PAYMENT_STATUS.PAID) entry.revenue += row.amount;
            entry.students.push({
                student: row.student_name !== null ? row.student_name : 'Unknown',
                paid: row.amount !== null ? row.amount : 0,
            });
        }
        return [...byCourse.values()];
    }
}

module.exports = ReportService;
