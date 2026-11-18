import { loadRecords, calcStats } from '../data/storage'

interface Props {
  onBack: () => void
}

export default function Stats({ onBack }: Props) {
  const records = loadRecords()
  const stats = calcStats(records)
  const hours = Math.floor(stats.totalMinutes / 60)
  const mins = stats.totalMinutes % 60

  // 柱状图最高值，用于换算高度
  const maxMinutes = Math.max(25, ...stats.last7.map((d) => d.minutes))

  return (
    <div className="page stats-page">
      <header className="topbar">
        <button className="link-btn" onClick={onBack}>← 返回</button>
        <div className="brand">
          <span className="brand-mark">熊</span>
          <span>小熊自习室</span>
        </div>
        <div style={{ width: 80 }} />
      </header>

      <main className="stats-main">
        <h1 className="stats-title">我的自习记录</h1>

        <div className="stat-cards">
          <div className="stat-card">
            <div className="stat-value">{hours}<small>时</small>{mins}<small>分</small></div>
            <div className="stat-label">累计专注</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.studyDays}<small>天</small></div>
            <div className="stat-label">打卡天数</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.streak}<small>天</small></div>
            <div className="stat-label">连续打卡</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.totalSessions}<small>次</small></div>
            <div className="stat-label">完成次数</div>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-title">最近 7 天的专注</div>
          <div className="chart">
            {stats.last7.map((d, i) => (
              <div className="chart-col" key={i}>
                <div className="chart-bar-wrap">
                  <div
                    className={'chart-bar ' + (d.minutes > 0 ? 'has-data' : '')}
                    style={{ height: `${(d.minutes / maxMinutes) * 100}%` }}
                    title={`${d.minutes} 分钟`}
                  />
                </div>
                <div className="chart-label">{d.label}</div>
              </div>
            ))}
          </div>
        </div>

        {records.length === 0 && (
          <p className="stats-empty">还没有记录，去选一只熊开始第一段专注吧。</p>
        )}

        <button className="primary-btn stats-start" onClick={onBack}>开始自习</button>
      </main>
    </div>
  )
}
