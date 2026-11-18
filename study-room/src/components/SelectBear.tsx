import { bears, getBearImage, type BearId } from '../data/bears'

interface Props {
  onSelect: (id: BearId) => void
  onGoStats: () => void
}

export default function SelectBear({ onSelect, onGoStats }: Props) {
  return (
    <div className="page select-page">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">熊</span>
          <span>小熊自习室</span>
        </div>
        <button className="link-btn" onClick={onGoStats}>我的记录 →</button>
      </header>

      <main className="select-main">
        <h1 className="select-title">选一只熊，陪你自习</h1>
        <p className="select-subtitle">不同的伙伴有不同的陪学风格，选一个今天合你心意的</p>

        <div className="bear-grid">
          {bears.map((bear) => (
            <button
              key={bear.id}
              className="bear-card"
              onClick={() => onSelect(bear.id)}
            >
              <div className="bear-card-img">
                <img src={getBearImage(bear.id, 'idle')} alt={bear.name} />
              </div>
              <div className="bear-card-name">{bear.name}</div>
              <div className="bear-card-style">{bear.style}</div>
              <div className="bear-card-desc">{bear.desc}</div>
              <div className="bear-card-cta">选 TA 陪我</div>
            </button>
          ))}
        </div>
      </main>

      <footer className="select-footer">数据只保存在你自己的浏览器里，不会上传</footer>
    </div>
  )
}
