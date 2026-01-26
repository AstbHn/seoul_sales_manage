from flask import jsonify
from werkzeug.exceptions import HTTPException
from service import main

def register_error_handlers(app):

    # ===============================
    # 공통 에러 (모든 Exception)
    # ===============================
    @app.errorhandler(Exception)
    def handle_exception(e):
        print(f"[{main.time_stamp()}] [ERROR] {repr(e)}")

        if isinstance(e, HTTPException):
            return jsonify({
                "status": e.code,
                "error": e.name,
                "message": e.description
            }), e.code

        return jsonify({
            "status": 500,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "서버 내부 오류 발생"
        }), 500


    # ===============================
    # 파일 없음 (CSV, PDF)
    # ===============================
    @app.errorhandler(FileNotFoundError)
    def handle_file_not_found(e):
        return jsonify({
            "status": 404,
            "error": "FILE_NOT_FOUND",
            "message": str(e)
        }), 404


    # ===============================
    # 데이터 오류 (JSON, 타입)
    # ===============================
    @app.errorhandler(ValueError)
    @app.errorhandler(TypeError)
    @app.errorhandler(KeyError)
    def handle_bad_request(e):
        return jsonify({
            "status": 400,
            "error": "BAD_REQUEST",
            "message": str(e)
        }), 400
