from sqlmodel import Session, create_engine
from app.core.config import settings
import libsql_client

# 1. Turso公式クライアント (HTTPモードで接続を安定化)
raw_url = settings.DATABASE_URL.replace("libsql://", "https://").replace("wss://", "https://")
client = libsql_client.create_client_sync(url=raw_url, auth_token=settings.TURSO_TOKEN)

# 2. 辞書・インデックス・ドットアクセス・数値比較・型変換すべてに対応する万能Row
class TursoRow(dict):
    """辞書・プロパティ・数値計算（左右両対応）を網羅する究極のRow"""
    def __init__(self, data, columns):
        super().__init__(data)
        self.columns = columns
        self.data_list = [data[col] for col in columns]

    def __getattr__(self, name):
        if name in self: return self[name]
        raise AttributeError(f"'TursoRow' has no attribute '{name}'")

    def __getitem__(self, key):
        if isinstance(key, int): return self.data_list[key]
        return super().__getitem__(key)

    def _get_scalar(self):
        val = self.data_list[0] if self.data_list else 0
        return val if val is not None else 0

    # 数値変換
    def __int__(self): return int(self._get_scalar())
    def __float__(self): return float(self._get_scalar())
    def __index__(self): return int(self._get_scalar())

    # --- 四則演算（左側：self op other） ---
    def __add__(self, other): return self._get_scalar() + (other._get_scalar() if hasattr(other, '_get_scalar') else other)
    def __sub__(self, other): return self._get_scalar() - (other._get_scalar() if hasattr(other, '_get_scalar') else other)
    def __mul__(self, other): return self._get_scalar() * (other._get_scalar() if hasattr(other, '_get_scalar') else other)
    def __truediv__(self, other):
        o = other._get_scalar() if hasattr(other, '_get_scalar') else other
        return self._get_scalar() / o if o != 0 else 0

    # --- 四則演算（右側：other op self） ---
    def __radd__(self, other): return other + self._get_scalar()
    def __rsub__(self, other): return other - self._get_scalar()
    def __rmul__(self, other): return other * self._get_scalar()
    def __rtruediv__(self, other):
        s = self._get_scalar()
        return other / s if s != 0 else 0

    # 比較演算
    def __gt__(self, other): return self._get_scalar() > (other if not hasattr(other, '_get_scalar') else int(other))
    def __lt__(self, other): return self._get_scalar() < (other if not hasattr(other, '_get_scalar') else int(other))
    def __eq__(self, other):
        if isinstance(other, (int, float)): return self._get_scalar() == other
        return super().__eq__(other)

class TursoResult:
    def __init__(self, res):
        self.columns = res.columns
        self._rows = [TursoRow({col: row[i] for i, col in enumerate(self.columns)}, self.columns) for row in res.rows]
    def all(self): return self._rows
    def first(self): return self._rows[0] if self._rows else None
    def scalar(self): return self._rows[0]._get_scalar() if self._rows else 0

# 3. 登録(INSERT)とフラッシュを管理する最強プロキシ
class TursoSessionProxy:
    def __init__(self, client):
        self.client = client
        self._to_add = []

    def exec(self, query):
        # SQLModelのクエリを文字列化して直送
        sql = str(query.compile(compile_kwargs={"literal_binds": True}))
        res = self.client.execute(sql)
        return TursoResult(res)

    def add(self, obj):
        self._to_add.append(obj)

    def flush(self):
        # AI解析時に呼ばれる事があるため定義（commitで一括処理するため空でOK）
        pass

class TursoSessionProxy:
    def __init__(self, client):
        self.client = client
        self._to_add = []     # 新規または更新用
        self._to_delete = []  # 削除用

    def exec(self, query):
        sql = str(query.compile(compile_kwargs={"literal_binds": True}))
        res = self.client.execute(sql)
        return TursoResult(res)

    def get(self, model, ident):
        table_name = model.__tablename__
        sql = f"SELECT * FROM {table_name} WHERE id = {ident}"
        res = self.client.execute(sql)
        row = TursoResult(res).first()
        if row:
            # 取得した行にテーブル名を覚えさせる（削除時に必要）
            row.__tablename__ = table_name
        return row

    def add(self, obj):
        self._to_add.append(obj)

    def delete(self, obj):
        self._to_delete.append(obj)

    def flush(self): pass

    def commit(self):
        # 1. 削除処理
        for obj in self._to_delete:
            # obj が __tablename__ を持っているか、直接指定されているか確認
            table_name = getattr(obj, '__tablename__', None)
            ident = obj.get('id') if isinstance(obj, dict) else getattr(obj, 'id', None)
            
            if table_name and ident:
                sql = f"DELETE FROM {table_name} WHERE id = {ident}"
                print(f"📡 Executing Cloud DELETE: {sql}")
                self.client.execute(sql)
        self._to_delete = []

        # 2. 登録・更新処理
        for obj in self._to_add:
            fields = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
            table_name = obj.__tablename__
            ident = fields.get('id')

            # --- ここが「更新」の肝 ---
            if ident: # IDがある場合は UPDATE
                update_pairs = []
                for k, v in fields.items():
                    if k == "id": continue
                    val = "NULL" if v is None else (str(v) if isinstance(v, (int, float)) else f"'{str(v).replace("'", "''")}'")
                    update_pairs.append(f"{k} = {val}")
                sql = f"UPDATE {table_name} SET {', '.join(update_pairs)} WHERE id = {ident}"
            else: # IDがない場合は INSERT
                cols = [k for k in fields.keys() if k != "id"]
                vals = []
                for k in cols:
                    v = fields[k]
                    vals.append("NULL" if v is None else (str(v) if isinstance(v, (int, float)) else f"'{str(v).replace("'", "''")}'"))
                sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(vals)})"
            
            res = self.client.execute(sql)
            if not ident and hasattr(res, 'last_insert_rowid'):
                obj.id = res.last_insert_rowid

        self._to_add = []

    def refresh(self, obj): pass
    def close(self): pass

# ダミーEngine (判定用)
engine = create_engine("sqlite://", creator=lambda: None) 

def get_db():
    if "turso.io" in settings.DATABASE_URL:
        yield TursoSessionProxy(client)
    else:
        with Session(engine) as session:
            yield session

get_session = get_db