const sqlite3 = require('sqlite3');

class Database {
    constructor(file) {
        this.conn = new sqlite3.Database(file);
        this.txQueue = Promise.resolve();
    }

    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.conn.run(sql, params, function (err) {
                if (err) return reject(err);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.conn.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.conn.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
        });
    }

    // Transações são serializadas porque a conexão SQLite é única.
    transaction(work) {
        const result = this.txQueue.then(async () => {
            await this.run('BEGIN');
            try {
                const value = await work();
                await this.run('COMMIT');
                return value;
            } catch (err) {
                await this.run('ROLLBACK');
                throw err;
            }
        });
        this.txQueue = result.catch(() => {});
        return result;
    }
}

module.exports = Database;
