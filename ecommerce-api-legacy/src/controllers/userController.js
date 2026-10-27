class UserController {
    constructor({ userModel }) {
        this.userModel = userModel;
        this.remove = this.remove.bind(this);
    }

    async remove(req, res, next) {
        try {
            await this.userModel.deleteWithDependents(req.params.id);
            res.send('Usuário deletado junto com suas matrículas e pagamentos.');
        } catch (err) {
            next(err);
        }
    }
}

module.exports = UserController;
