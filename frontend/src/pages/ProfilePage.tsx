import { UserOutlined } from '@ant-design/icons'
import FeaturePage from '../components/function-ui/FeaturePage'
import AvatarSection from '../features/profile/AvatarSection'
import ProfileInfoSection from '../features/profile/ProfileInfoSection'

export default function ProfilePage() {
  return (
    <FeaturePage
      eyebrow="Tài khoản"
      title="Hồ sơ cá nhân"
      description="Quản lý thông tin liên hệ và ảnh đại diện của tài khoản. Email và vai trò được quản lý bởi quản trị hệ thống."
      icon={<UserOutlined />}
      tone="blue"
      className="profile-feature-page"
    >
      <section className="profile-premium-grid">
        <AvatarSection />

        <div className="profile-premium-main">
          <div className="profile-premium-card profile-info-card">
            <div className="profile-premium-card-head">
              <div>
                <span className="profile-card-kicker">Thông tin tài khoản</span>
                <h2>Thông tin cá nhân</h2>
                <p>Cập nhật thông tin liên hệ dùng trong hệ thống đào tạo.</p>
              </div>
            </div>

            <div className="profile-premium-card-body">
              <ProfileInfoSection />
            </div>
          </div>
        </div>
      </section>
    </FeaturePage>
  )
}
