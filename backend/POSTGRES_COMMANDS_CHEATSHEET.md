# PostgreSQL Testing Commands - Copy & Paste Cheat Sheet

## Quick Commands (Copy & Paste)

### 1. Test Connection
```bash
psql -U socialhub -d socialhub_db -c "SELECT version();"
```

### 2. List All Tables
```bash
psql -U socialhub -d socialhub_db -c "\dt"
```

### 3. Count All Records
```bash
psql -U socialhub -d socialhub_db -c "SELECT COUNT(*) as total_users FROM users;"
```

### 4. View All Users
```bash
psql -U socialhub -d socialhub_db -c "SELECT id, email, full_name, auth_provider, created_at FROM users;"
```

### 5. View User Details
```bash
psql -U socialhub -d socialhub_db -c "SELECT * FROM users WHERE email = 'test@example.com';"
```

### 6. View All Groups
```bash
psql -U socialhub -d socialhub_db -c "SELECT id, name, description, created_by, created_at FROM groups;"
```

### 7. View Group Members
```bash
psql -U socialhub -d socialhub_db -c "
  SELECT 
    g.name as group_name,
    u.full_name as member_name,
    gm.joined_at
  FROM groups g
  JOIN group_members gm ON g.id = gm.group_id
  JOIN users u ON gm.user_id = u.id;
"
```

### 8. View Messages
```bash
psql -U socialhub -d socialhub_db -c "SELECT id, user_id, message, created_at FROM chat_messages LIMIT 10;"
```

### 9. View Pinned Messages
```bash
psql -U socialhub -d socialhub_db -c "SELECT id, message_id, room_name, pinned_by, pinned_at FROM pinned_messages;"
```

### 10. Comprehensive Test (ALL IN ONE)
```bash
psql -U socialhub -d socialhub_db << SQL
\echo '===== POSTGRESQL DATABASE STATUS ====='
\echo ''
SELECT version() as "PostgreSQL Version";
\echo ''
\echo 'Tables:'
\dt
\echo ''
\echo 'Record Counts:'
SELECT 
  'users' as table_name, COUNT(*) FROM users
UNION ALL
SELECT 'groups', COUNT(*) FROM groups
UNION ALL
SELECT 'group_members', COUNT(*) FROM group_members
UNION ALL
SELECT 'chat_messages', COUNT(*) FROM chat_messages
UNION ALL
SELECT 'pinned_messages', COUNT(*) FROM pinned_messages;
\echo ''
\echo 'Users:'
SELECT id, email, full_name FROM users LIMIT 5;
SQL
```

### 11. Interactive Mode (Type \q to quit)
```bash
psql -U socialhub -d socialhub_db
```

### 12. Backup Database
```bash
pg_dump -U socialhub -d socialhub_db > socialhub_backup.sql
```

### 13. View Table Structure
```bash
psql -U socialhub -d socialhub_db -c "\d users"
```

### 14. Check Database Size
```bash
psql -U socialhub -d socialhub_db -c "
  SELECT 
    tablename, 
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
  FROM pg_tables 
  WHERE schemaname = 'public';
"
```

---

## Connection Details
- **Host**: localhost
- **Port**: 5432
- **Database**: socialhub_db
- **User**: socialhub
- **Password**: socialhub_pass

---

## Common Psql Commands (Interactive Mode)

Run `psql -U socialhub -d socialhub_db` then:

```
\dt          - List all tables
\d users     - Show users table structure
\d groups    - Show groups table structure
SELECT * FROM users;     - View all users
SELECT * FROM groups;    - View all groups
\du          - List all users
\l           - List all databases
\q           - Quit
```

---

## Status Right Now

✅ PostgreSQL 15.13 running
✅ 5 tables created (users, groups, group_members, chat_messages, pinned_messages)
✅ All tables empty (0 records)
✅ Ready for data

Ready to register users and test!
