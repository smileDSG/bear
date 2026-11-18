import { findBear, getBearImage, type BearId } from '../data/bears'

interface Props {
  bearId: BearId
  minutes: number
  onAgain: () => void
  onGoStats: () => void
  onBackHome: () => void
}

export default function Complete({ bearId, minutes, onAgain, onGoStats, onBackHome }: Props) {
  const bear = findBear(bearId)
  return (
    <div className="page complete-page">
      <div className="complete-card">
        <div className="complete-badge">打卡成功</div>
        <img className="complete-bear" src={getBearImage(bearId, 'done')} alt={bear.name} />
        <div className="speech complete-speech">
          <span className="speech-name">{bear.name}</span>
          <span className="speech-text">{bear.lines.done}</span>
        </div>
        <h1 className="complete-title">这一段专注，完成了</h1>
        <div className="complete-minutes"><strong>{minutes}</strong> 分钟</div>
        <p className="complete-note">已经记到你的自习档案里，去看看积累了多少吧</p>

        <div className="complete-actions">
          <button className="primary-btn" onClick={onAgain}>再来一段</button>
          <button className="secondary-btn" onClick={onGoStats}>看我的记录</button>
        </div>
        <button className="link-btn" onClick={onBackHome}>回到首页</button>
      </div>
    </div>
  )
}
