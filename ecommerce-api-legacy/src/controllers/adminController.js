class AdminController {
    constructor({ reportService }) {
        this.reportService = reportService;
        this.financialReport = this.financialReport.bind(this);
    }

    async financialReport(req, res, next) {
        try {
            res.json(await this.reportService.financialReport());
        } catch (err) {
            next(err);
        }
    }
}

module.exports = AdminController;
