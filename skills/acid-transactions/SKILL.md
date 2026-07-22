---
name: acid-transactions
description: Use when writing business logic with database transactions, detecting race conditions, implementing retry/rollback patterns, choosing isolation levels, or debugging concurrency issues. Also use when building financial, booking, inventory, or any multi-step write operations. Use ONLY when database/state mutation transactions are involved — not for simple CRUD without transactional concerns.
---

# ACID Transactions for Business Logic

Patterns dan implementation untuk transaksi database yang benar. Mencegah race condition, data corruption, dan inconsistency.

## Overview

ACID bukan hanya teori database — ini contract yang harus di-enforce di kode aplikasi. Setiap operasi yang mengubah state harus bisa di-rollback secara konsisten.

## Pattern 1: Transaction Boundary

Operasi multi-step WAJIB wrapping transaction:

```typescript
// ❌ BAD: race condition — read after write tanpa transaction
async function transfer(fromId: string, toId: string, amount: number) {
  const from = await db.get(fromId)  // read
  from.balance -= amount
  await db.save(from)                // write
  // ↑ crash di sini: uang hilang, tidak sampai ke toId

  const to = await db.get(toId)
  to.balance += amount
  await db.save(to)
}
```

```typescript
// ✅ GOOD: atomic transaction
async function transfer(fromId: string, toId: string, amount: number) {
  const tx = await db.beginTransaction()   // BEGIN
  try {
    const from = await tx.get(fromId, { lock: 'FOR UPDATE' })  // lock row
    if (from.balance < amount) throw new InsufficientBalance()
    await tx.update(fromId, { balance: from.balance - amount })

    const to = await tx.get(toId, { lock: 'FOR UPDATE' })
    await tx.update(toId, { balance: to.balance + amount })

    await tx.commit()                       // COMMIT — durable
  } catch (err) {
    await tx.rollback()                     // ROLLBACK — consistent
    throw err
  }
}
```

## Pattern 2: Isolation Level Selection

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Use Case |
|---|---|---|---|---|
| READ UNCOMMITTED | ✅ Mungkin | ✅ Mungkin | ✅ Mungkin | Reporting kasar, never untuk bisnis logic |
| READ COMMITTED | ❌ Tidak | ✅ Mungkin | ✅ Mungkin | Default. Cocok untuk read-heavy |
| REPEATABLE READ | ❌ Tidak | ❌ Tidak | ✅ Mungkin | Invoice, saldo — butuh repeatable read |
| SERIALIZABLE | ❌ Tidak | ❌ Tidak | ❌ Tidak | Booking, financial transfer — zero tolerance |

**Rule of thumb:**
- SERIALIZABLE: mutasi saldo, booking, inventory deduction
- REPEATABLE READ: baca transaksi untuk ditampilkan
- READ COMMITTED: query biasa
- READ UNCOMMITTED: **jangan pernah** untuk bisnis logic

## Pattern 3: Optimistic vs Pessimistic Locking

### Optimistic Locking (version field)

```typescript
// ✅ GOOD: conflict terdeteksi saat commit
async function updateProfile(userId: string, data: Profile, version: number) {
  const result = await db.execute(
    `UPDATE profiles SET name = ?, version = version + 1
     WHERE user_id = ? AND version = ?`,
    [data.name, userId, version]
  )
  if (result.affectedRows === 0) {
    throw new OptimisticLockError('Profile modified by another request')
  }
}
```

### Pessimistic Locking (SELECT FOR UPDATE)

Gunakan ketika conflict tinggi dan retry mahal:

```sql
BEGIN;
SELECT * FROM orders WHERE id = ? FOR UPDATE;
-- proses order...
UPDATE orders SET status = 'processed' WHERE id = ?;
COMMIT;
```

## Pattern 4: Distributed Transaction (XA / Saga)

Untuk microservices — jangan pake XA transaction lintas service. Gunakan Saga pattern:

```typescript
// Saga: Compensating Transaction
async function placeOrder(order: Order) {
  const saga = {
    steps: [
      { action: () => reserveInventory(order.items), compensate: () => releaseInventory(order.items) },
      { action: () => chargePayment(order.total),    compensate: () => refund(order.total) },
      { action: () => updateOrderStatus(order.id),   compensate: () => rollbackOrderStatus(order.id) },
    ]
  }

  const executed = []
  for (const step of saga.steps) {
    try {
      await step.action()
      executed.push(step)
    } catch (err) {
      // ROLLBACK: execute compensating actions in reverse order
      for (const s of executed.reverse()) {
        await s.compensate()
      }
      throw err
    }
  }
}
```

## Pattern 5: Retry dengan Exponential Backoff

Untuk transient failure (deadlock, timeout) — jangan retry untuk business error:

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  options: { maxRetries?: number; baseDelay?: number } = {}
): Promise<T> {
  const { maxRetries = 3, baseDelay = 100 } = options
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (err) {
      if (attempt === maxRetries) throw err
      // Only retry transient errors
      if (!isTransientError(err)) throw err
      const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 100
      await sleep(delay)
    }
  }
  throw new Error('Unreachable')
}

function isTransientError(err: unknown): boolean {
  const msg = String(err).toLowerCase()
  return msg.includes('deadlock') || msg.includes('timeout') ||
         msg.includes('too many connections') || msg.includes('serialization failure')
}
```

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Transaction per row dalam loop | N + 1 transactions, slow | Batch dalam 1 transaction |
| AUTOCOMMIT = true + manual rollback | Rollback tidak efektif | Explicit BEGIN/COMMIT |
| Read tanpa lock lalu write | Race condition | SELECT FOR UPDATE atau optimistic lock |
| Transaction terlalu panjang | Lock contention, deadlock | Minimal scope, split jika perlu |
| Retry business error | Order duplikat, overcharge | Retry ONLY transient errors |
| Nested transaction | DB tidak support (MySQL rollback semua) | Savepoint atau rewrite tanpa nested |

## Red Flags (STOP + audit)

- `read-modify-write` cycle tanpa lock atau transaction wrapper
- `UPDATE ... WHERE` tanpa version check atau row lock
- Retry tanpa bedakan transient vs business error
- Operasi lintas service dalam 1 transaction DB
- Timeout terlalu pendek untuk slow transaction

## Debugging Transaction Issues

```
1. Deadlock → cek log: mysql> SHOW ENGINE INNODB STATUS
   Fix: konsisten urutan akses row, kurangi transaction length

2. Dirty read → isolation level too low
   Fix: set REPEATABLE READ atau SERIALIZABLE

3. Lost update → no lock, no version
   Fix: SELECT FOR UPDATE atau optimistic locking

4. Phantom read → inconsistent dalam 1 transaction
   Fix: SERIALIZABLE atau range lock
```

## Verification Checklist

- [ ] Setiap multi-step write dibungkus transaction
- [ ] Rollback handler untuk setiap BEGIN
- [ ] Isolation level sesuai kebutuhan (bukan default buta)
- [ ] Lock strategy: optimistic vs pessimistic sudah dipilih
- [ ] Tidak ada N+1 transaction dalam loop
- [ ] Retry hanya untuk transient error
- [ ] Non-repudiation: ada log sebelum commit