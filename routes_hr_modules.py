"""
招聘、培训、离职管理模块 API
"""
from flask import request, jsonify, g
import sqlite3
import datetime

def register_hr_modules(app, get_db, log_operation, require_permission, require_login):
    """注册人力资源管理模块API"""
    
    # ============================================================
    # 招聘管理 API
    # ============================================================
    
    @app.route('/api/recruitment/positions', methods=['GET', 'POST'])
    @require_permission('personnel', 'write')
    def recruitment_positions():
        """获取或创建招聘岗位"""
        db = get_db()
        
        if request.method == 'GET':
            status = request.args.get('status', '')
            dept = request.args.get('department', '')
            
            conditions = []
            params = []
            
            if status:
                conditions.append("status=?")
                params.append(status)
            if dept:
                conditions.append("department=?")
                params.append(dept)
            
            where = " WHERE " + " AND ".join(conditions) if conditions else ""
            rows = db.execute(f"SELECT * FROM recruitment_positions{where} ORDER BY created_at DESC", params).fetchall()
            
            result = []
            for r in rows:
                d = dict(r)
                # 获取创建人姓名
                creator = db.execute("SELECT real_name FROM users WHERE id=?", (d['created_by'],)).fetchone()
                d['creator_name'] = creator['real_name'] if creator else ''
                result.append(d)
            
            return jsonify(result)
        
        # POST - 创建岗位
        data = request.json or {}
        if not data.get('position_name') or not data.get('department'):
            return jsonify({'error': '岗位名称和科室不能为空'}), 400
        
        db.execute("""INSERT INTO recruitment_positions 
            (position_name, department, headcount, requirements, status, publish_date, deadline, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                   (data['position_name'], data['department'], data.get('headcount', 1),
                    data.get('requirements'), data.get('status', '招聘中'),
                    data.get('publish_date'), data.get('deadline'), g.current_user['user_id']))
        db.commit()
        
        log_operation('创建招聘岗位', 'recruitment', data['position_name'])
        return jsonify({'ok': True})
    
    @app.route('/api/recruitment/positions/<int:pos_id>', methods=['PUT', 'DELETE'])
    @require_permission('personnel', 'write')
    def update_recruitment_position(pos_id):
        """更新或删除招聘岗位"""
        db = get_db()
        
        if request.method == 'DELETE':
            db.execute("UPDATE recruitment_positions SET status='已关闭' WHERE id=?", (pos_id,))
            db.commit()
            log_operation('关闭招聘岗位', 'recruitment', f'ID:{pos_id}')
            return jsonify({'ok': True})
        
        # PUT - 更新
        data = request.json or {}
        db.execute("""UPDATE recruitment_positions SET position_name=?, department=?, headcount=?,
            hired_count=?, requirements=?, status=?, publish_date=?, deadline=? WHERE id=?""",
                   (data.get('position_name'), data.get('department'), data.get('headcount'),
                    data.get('hired_count'), data.get('requirements'), data.get('status'),
                    data.get('publish_date'), data.get('deadline'), pos_id))
        db.commit()
        
        log_operation('更新招聘岗位', 'recruitment', data.get('position_name', ''))
        return jsonify({'ok': True})
    
    @app.route('/api/recruitment/applicants', methods=['GET', 'POST'])
    @require_permission('personnel', 'write')
    def recruitment_applicants():
        """获取或创建应聘者信息"""
        db = get_db()
        
        if request.method == 'GET':
            position_id = request.args.get('position_id', '')
            status = request.args.get('status', '')
            
            conditions = []
            params = []
            
            if position_id:
                conditions.append("a.position_id=?")
                params.append(position_id)
            if status:
                conditions.append("a.status=?")
                params.append(status)
            
            where = " WHERE " + " AND ".join(conditions) if conditions else ""
            rows = db.execute(f"""SELECT a.*, p.position_name, p.department
                FROM applicants a JOIN recruitment_positions p ON a.position_id=p.id
                {where} ORDER BY a.applied_at DESC""", params).fetchall()
            
            return jsonify([dict(r) for r in rows])
        
        # POST - 创建应聘者
        data = request.json or {}
        if not data.get('name') or not data.get('position_id'):
            return jsonify({'error': '姓名和岗位不能为空'}), 400
        
        from app import aes_encrypt
        db.execute("""INSERT INTO applicants 
            (position_id, name, gender, birth_date, phone_encrypted, email, education, major, experience_years, resume_path, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                   (data['position_id'], data['name'], data.get('gender'), data.get('birth_date'),
                    aes_encrypt(data.get('phone', '')), data.get('email'), data.get('education'),
                    data.get('major'), data.get('experience_years'), data.get('resume_path'),
                    data.get('status', '待筛选')))
        db.commit()
        
        log_operation('录入应聘者', 'recruitment', data['name'])
        return jsonify({'ok': True})
    
    @app.route('/api/recruitment/applicants/<int:app_id>', methods=['PUT'])
    @require_permission('personnel', 'write')
    def update_applicant(app_id):
        """更新应聘者状态"""
        db = get_db()
        data = request.json or {}
        
        db.execute("UPDATE applicants SET status=? WHERE id=?", (data.get('status'), app_id))
        db.commit()
        
        log_operation('更新应聘者状态', 'recruitment', f'ID:{app_id}')
        return jsonify({'ok': True})
    
    @app.route('/api/recruitment/interviews', methods=['GET', 'POST'])
    @require_permission('personnel', 'write')
    def recruitment_interviews():
        """获取或创建面试记录"""
        db = get_db()
        
        if request.method == 'GET':
            applicant_id = request.args.get('applicant_id', '')
            conditions = ["i.applicant_id=?"] if applicant_id else []
            params = [applicant_id] if applicant_id else []
            
            where = " WHERE " + " AND ".join(conditions) if conditions else ""
            rows = db.execute(f"""SELECT i.*, a.name as applicant_name, u.real_name as interviewer_name
                FROM interviews i JOIN applicants a ON i.applicant_id=a.id
                LEFT JOIN users u ON i.interviewer_id=u.id
                {where} ORDER BY i.interview_date DESC""", params).fetchall()
            
            return jsonify([dict(r) for r in rows])
        
        # POST - 创建面试记录
        data = request.json or {}
        db.execute("""INSERT INTO interviews 
            (applicant_id, interview_type, interviewer_id, interview_date, score, comments, result)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                   (data['applicant_id'], data.get('interview_type'), data.get('interviewer_id'),
                    data.get('interview_date'), data.get('score'), data.get('comments'), data.get('result')))
        db.commit()
        
        log_operation('创建面试记录', 'recruitment', f"申请人ID:{data['applicant_id']}")
        return jsonify({'ok': True})
    
    @app.route('/api/recruitment/statistics', methods=['GET'])
    @require_permission('personnel', 'read')
    def recruitment_statistics():
        """招聘统计分析"""
        db = get_db()
        
        # 岗位统计
        positions = db.execute("""SELECT status, COUNT(*) as count 
            FROM recruitment_positions GROUP BY status""").fetchall()
        
        # 应聘者统计
        applicants = db.execute("""SELECT status, COUNT(*) as count 
            FROM applicants GROUP BY status""").fetchall()
        
        return jsonify({
            'positions': [dict(r) for r in positions],
            'applicants': [dict(r) for r in applicants],
        })
    
    # ============================================================
    # 培训管理 API
    # ============================================================
    
    @app.route('/api/training/plans', methods=['GET', 'POST'])
    @require_permission('personnel', 'write')
    def training_plans():
        """获取或创建培训计划"""
        db = get_db()
        
        if request.method == 'GET':
            status = request.args.get('status', '')
            conditions = ["status=?"] if status else []
            params = [status] if status else []
            
            where = " WHERE " + " AND ".join(conditions) if conditions else ""
            rows = db.execute(f"SELECT * FROM training_plans{where} ORDER BY start_date DESC", params).fetchall()
            
            return jsonify([dict(r) for r in rows])
        
        # POST - 创建培训计划
        data = request.json or {}
        if not data.get('title'):
            return jsonify({'error': '培训标题不能为空'}), 400
        
        db.execute("""INSERT INTO training_plans 
            (title, training_type, trainer, start_date, end_date, location, max_participants, description, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                   (data['title'], data.get('training_type'), data.get('trainer'),
                    data.get('start_date'), data.get('end_date'), data.get('location'),
                    data.get('max_participants'), data.get('description'),
                    data.get('status', '计划中'), g.current_user['user_id']))
        db.commit()
        
        log_operation('创建培训计划', 'training', data['title'])
        return jsonify({'ok': True})
    
    @app.route('/api/training/plans/<int:plan_id>', methods=['PUT', 'DELETE'])
    @require_permission('personnel', 'write')
    def update_training_plan(plan_id):
        """更新或删除培训计划"""
        db = get_db()
        
        if request.method == 'DELETE':
            db.execute("UPDATE training_plans SET status='已取消' WHERE id=?", (plan_id,))
            db.commit()
            log_operation('取消培训计划', 'training', f'ID:{plan_id}')
            return jsonify({'ok': True})
        
        # PUT - 更新
        data = request.json or {}
        db.execute("""UPDATE training_plans SET title=?, training_type=?, trainer=?, start_date=?,
            end_date=?, location=?, max_participants=?, description=?, status=? WHERE id=?""",
                   (data.get('title'), data.get('training_type'), data.get('trainer'),
                    data.get('start_date'), data.get('end_date'), data.get('location'),
                    data.get('max_participants'), data.get('description'),
                    data.get('status'), plan_id))
        db.commit()
        
        log_operation('更新培训计划', 'training', data.get('title', ''))
        return jsonify({'ok': True})
    
    @app.route('/api/training/enroll', methods=['POST'])
    @require_login
    def training_enroll():
        """职工报名培训"""
        data = request.json or {}
        plan_id = data.get('plan_id')
        emp_id = g.current_user['user_id']
        
        if not plan_id:
            return jsonify({'error': '请指定培训计划'}), 400
        
        db = get_db()
        
        try:
            db.execute("""INSERT INTO training_enrollments (plan_id, emp_id, enrollment_status)
                VALUES (?, ?, '已报名')""", (plan_id, emp_id))
            db.commit()
            
            # 更新报名人数
            db.execute("""UPDATE training_plans SET enrolled_count=enrolled_count+1 WHERE id=?""", (plan_id,))
            db.commit()
            
            log_operation('报名培训', 'training', f'计划ID:{plan_id}')
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'error': '报名失败，可能已报名'}), 400
    
    @app.route('/api/training/enrollments', methods=['GET'])
    @require_permission('personnel', 'read')
    def training_enrollments():
        """获取培训报名记录"""
        db = get_db()
        plan_id = request.args.get('plan_id', '')
        
        conditions = ["e.plan_id=?"] if plan_id else []
        params = [plan_id] if plan_id else []
        
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        rows = db.execute(f"""SELECT e.*, emp.name as emp_name, emp.emp_no, p.title as plan_title
            FROM training_enrollments e 
            JOIN employees emp ON e.emp_id=emp.id
            JOIN training_plans p ON e.plan_id=p.id
            {where} ORDER BY e.enrolled_at DESC""", params).fetchall()
        
        return jsonify([dict(r) for r in rows])
    
    @app.route('/api/training/records', methods=['GET', 'POST'])
    @require_permission('personnel', 'write')
    def training_records():
        """获取或创建培训档案"""
        db = get_db()
        
        if request.method == 'GET':
            emp_id = request.args.get('emp_id', '')
            conditions = ["emp_id=?"] if emp_id else []
            params = [emp_id] if emp_id else []
            
            where = " WHERE " + " AND ".join(conditions) if conditions else ""
            rows = db.execute(f"SELECT * FROM training_records{where} ORDER BY training_date DESC", params).fetchall()
            
            return jsonify([dict(r) for r in rows])
        
        # POST - 创建培训记录
        data = request.json or {}
        db.execute("""INSERT INTO training_records 
            (emp_id, training_name, training_type, training_date, hours, score, certificate_no, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                   (data['emp_id'], data['training_name'], data.get('training_type'),
                    data.get('training_date'), data.get('hours'), data.get('score'),
                    data.get('certificate_no'), data.get('description')))
        db.commit()
        
        log_operation('录入培训记录', 'training', data['training_name'])
        return jsonify({'ok': True})
    
    @app.route('/api/training/statistics', methods=['GET'])
    @require_permission('personnel', 'read')
    def training_statistics():
        """培训统计分析"""
        db = get_db()
        
        # 培训计划统计
        plans = db.execute("""SELECT status, COUNT(*) as count 
            FROM training_plans GROUP BY status""").fetchall()
        
        # 人均培训时长
        avg_hours = db.execute("""SELECT AVG(hours) as avg_hours 
            FROM training_records""").fetchone()
        
        return jsonify({
            'plans': [dict(r) for r in plans],
            'avg_training_hours': avg_hours['avg_hours'] if avg_hours else 0,
        })
    
    # ============================================================
    # 离职管理 API
    # ============================================================
    
    @app.route('/api/resignation/requests', methods=['GET', 'POST'])
    @require_permission('personnel', 'write')
    def resignation_requests():
        """获取或创建离职申请"""
        db = get_db()
        
        if request.method == 'GET':
            status = request.args.get('status', '')
            emp_id = request.args.get('emp_id', '')
            
            conditions = []
            params = []
            
            if status:
                conditions.append("r.status=?")
                params.append(status)
            if emp_id:
                conditions.append("r.emp_id=?")
                params.append(emp_id)
            
            where = " WHERE " + " AND ".join(conditions) if conditions else ""
            rows = db.execute(f"""SELECT r.*, emp.name as emp_name, emp.emp_no, emp.current_dept,
                u.real_name as approver_name
                FROM resignation_requests r 
                JOIN employees emp ON r.emp_id=emp.id
                LEFT JOIN users u ON r.approver_id=u.id
                {where} ORDER BY r.apply_date DESC""", params).fetchall()
            
            return jsonify([dict(r) for r in rows])
        
        # POST - 提交离职申请
        data = request.json or {}
        if not data.get('emp_id') or not data.get('resignation_type'):
            return jsonify({'error': '职工ID和离职类型不能为空'}), 400
        
        db.execute("""INSERT INTO resignation_requests 
            (emp_id, resignation_type, reason, apply_date, expected_last_day, status)
            VALUES (?, ?, ?, ?, ?, '待审批')""",
                   (data['emp_id'], data['resignation_type'], data.get('reason'),
                    data.get('apply_date'), data.get('expected_last_day')))
        db.commit()
        
        log_operation('提交离职申请', 'resignation', f"职工ID:{data['emp_id']}")
        return jsonify({'ok': True})
    
    @app.route('/api/resignation/requests/<int:req_id>', methods=['PUT'])
    @require_permission('personnel', 'write')
    def update_resignation_request(req_id):
        """更新离职申请状态"""
        db = get_db()
        data = request.json or {}
        
        db.execute("UPDATE resignation_requests SET status=? WHERE id=?", 
                   (data.get('status'), req_id))
        db.commit()
        
        log_operation('更新离职申请', 'resignation', f'ID:{req_id}')
        return jsonify({'ok': True})
    
    @app.route('/api/resignation/approve', methods=['POST'])
    @require_permission('personnel', 'write')
    def approve_resignation():
        """审批离职申请"""
        data = request.json or {}
        req_id = data.get('request_id')
        approved = data.get('approved', False)
        
        if not req_id:
            return jsonify({'error': '请指定申请ID'}), 400
        
        db = get_db()
        status = '已批准' if approved else '已拒绝'
        
        db.execute("""UPDATE resignation_requests SET status=?, approver_id=?, approved_at=?
            WHERE id=?""", (status, g.current_user['user_id'], 
                           datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), req_id))
        db.commit()
        
        log_operation('审批离职申请', 'resignation', f'ID:{req_id}, 结果:{status}')
        return jsonify({'ok': True})
    
    @app.route('/api/resignation/handover', methods=['GET', 'POST'])
    @require_permission('personnel', 'write')
    def resignation_handover():
        """获取或创建交接清单"""
        db = get_db()
        
        if request.method == 'GET':
            resignation_id = request.args.get('resignation_id', '')
            conditions = ["resignation_id=?"] if resignation_id else []
            params = [resignation_id] if resignation_id else []
            
            where = " WHERE " + " AND ".join(conditions) if conditions else ""
            rows = db.execute(f"SELECT * FROM resignation_handover{where}", params).fetchall()
            
            return jsonify([dict(r) for r in rows])
        
        # POST - 创建交接项
        data = request.json or {}
        db.execute("""INSERT INTO resignation_handover 
            (resignation_id, item_name, item_type, status, handler_id, remarks)
            VALUES (?, ?, ?, '待交接', ?, ?)""",
                   (data['resignation_id'], data['item_name'], data.get('item_type'),
                    data.get('handler_id'), data.get('remarks')))
        db.commit()
        
        log_operation('创建交接项', 'resignation', data['item_name'])
        return jsonify({'ok': True})
    
    @app.route('/api/resignation/handover/<int:item_id>', methods=['PUT'])
    @require_permission('personnel', 'write')
    def update_handover_item(item_id):
        """完成交接项"""
        db = get_db()
        
        db.execute("""UPDATE resignation_handover SET status='已完成', completed_at=?
            WHERE id=?""", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), item_id))
        db.commit()
        
        log_operation('完成交接项', 'resignation', f'ID:{item_id}')
        return jsonify({'ok': True})
    
    @app.route('/api/resignation/records', methods=['GET', 'POST'])
    @require_permission('personnel', 'write')
    def resignation_records():
        """获取或创建离职档案"""
        db = get_db()
        
        if request.method == 'GET':
            emp_id = request.args.get('emp_id', '')
            conditions = ["emp_id=?"] if emp_id else []
            params = [emp_id] if emp_id else []
            
            where = " WHERE " + " AND ".join(conditions) if conditions else ""
            rows = db.execute(f"SELECT * FROM resignation_records{where} ORDER BY created_at DESC", params).fetchall()
            
            return jsonify([dict(r) for r in rows])
        
        # POST - 创建离职档案
        data = request.json or {}
        db.execute("""INSERT INTO resignation_records 
            (emp_id, resignation_type, last_working_day, final_salary, handover_completed, exit_interview_notes)
            VALUES (?, ?, ?, ?, ?, ?)""",
                   (data['emp_id'], data.get('resignation_type'), data.get('last_working_day'),
                    data.get('final_salary'), data.get('handover_completed', 0),
                    data.get('exit_interview_notes')))
        db.commit()
        
        log_operation('创建离职档案', 'resignation', f"职工ID:{data['emp_id']}")
        return jsonify({'ok': True})
    
    @app.route('/api/resignation/statistics', methods=['GET'])
    @require_permission('personnel', 'read')
    def resignation_statistics():
        """离职统计分析"""
        db = get_db()
        
        # 离职类型统计
        types = db.execute("""SELECT resignation_type, COUNT(*) as count 
            FROM resignation_records GROUP BY resignation_type""").fetchall()
        
        # 离职率（最近一年）
        one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        total_emp = db.execute("SELECT COUNT(*) as count FROM employees WHERE status='在职'").fetchone()
        resigned = db.execute("""SELECT COUNT(*) as count FROM resignation_records 
            WHERE last_working_day >= ?""", (one_year_ago,)).fetchone()
        
        turnover_rate = (resigned['count'] / total_emp['count'] * 100) if total_emp['count'] > 0 else 0
        
        return jsonify({
            'types': [dict(r) for r in types],
            'turnover_rate': round(turnover_rate, 2),
            'resigned_count': resigned['count'],
            'total_employees': total_emp['count'],
        })
