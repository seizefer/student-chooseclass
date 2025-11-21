<!--
消息编写页面
@version: v1.0.0
@date: 2024-12-06
-->
<template>
  <div class="compose-message">
    <div class="page-header">
      <h1>编写消息</h1>
      <div class="header-actions">
        <el-button @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
    </div>

    <div class="compose-container">
      <el-card class="compose-card">
        <el-form
          ref="messageFormRef"
          :model="messageForm"
          :rules="formRules"
          label-width="80px"
          label-position="left"
        >
          <el-form-item label="收件人" prop="recipient">
            <el-select
              v-model="messageForm.recipient"
              placeholder="选择收件人"
              filterable
              allow-create
              style="width: 100%"
            >
              <el-option
                v-for="contact in contacts"
                :key="contact.id"
                :label="contact.name"
                :value="contact.name"
              >
                <span style="float: left">{{ contact.name }}</span>
                <span style="float: right; color: var(--text-color-secondary); font-size: 13px">
                  {{ contact.type }}
                </span>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="主题" prop="subject">
            <el-input
              v-model="messageForm.subject"
              placeholder="请输入消息主题"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="内容" prop="content">
            <div class="editor-container">
              <div class="editor-toolbar">
                <el-button-group>
                  <el-button size="small" @click="insertFormat('bold')">
                    <el-icon><DArrowRight /></el-icon>
                    粗体
                  </el-button>
                  <el-button size="small" @click="insertFormat('italic')">
                    <el-icon><DArrowRight /></el-icon>
                    斜体
                  </el-button>
                </el-button-group>
                
                <el-button size="small" @click="insertTemplate">
                  <el-icon><Document /></el-icon>
                  使用模板
                </el-button>
              </div>
              
              <el-input
                v-model="messageForm.content"
                type="textarea"
                :rows="12"
                placeholder="请输入消息内容..."
                maxlength="2000"
                show-word-limit
                resize="vertical"
              />
            </div>
          </el-form-item>

          <el-form-item label="附件">
            <el-upload
              ref="uploadRef"
              :file-list="fileList"
              :auto-upload="false"
              :show-file-list="true"
              multiple
              drag
              accept=".jpg,.png,.pdf,.doc,.docx,.txt"
              @change="handleFileChange"
              @remove="handleFileRemove"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 jpg/png/pdf/doc/txt 文件，单个文件不超过10MB
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <el-form-item label="发送选项">
            <el-checkbox-group v-model="messageForm.options">
              <el-checkbox value="receipt">要求已读回执</el-checkbox>
              <el-checkbox value="urgent">标记为紧急</el-checkbox>
              <el-checkbox value="draft">保存为草稿</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item>
            <div class="form-actions">
              <el-button
                type="primary"
                :loading="sending"
                @click="sendMessage"
              >
                <el-icon><Position /></el-icon>
                发送消息
              </el-button>
              
              <el-button @click="saveDraft">
                <el-icon><Document /></el-icon>
                保存草稿
              </el-button>
              
              <el-button @click="resetForm">
                <el-icon><RefreshRight /></el-icon>
                重置
              </el-button>
            </div>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 消息模板选择对话框 -->
      <el-dialog
        v-model="templateDialogVisible"
        title="选择消息模板"
        width="500px"
      >
        <el-row :gutter="16">
          <el-col
            v-for="template in messageTemplates"
            :key="template.id"
            :span="24"
            style="margin-bottom: 12px"
          >
            <el-card
              class="template-card"
              :class="{ selected: selectedTemplate?.id === template.id }"
              @click="selectTemplate(template)"
            >
              <h4>{{ template.title }}</h4>
              <p class="template-preview">{{ template.preview }}</p>
            </el-card>
          </el-col>
        </el-row>
        
        <template #footer>
          <el-button @click="templateDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :disabled="!selectedTemplate"
            @click="applyTemplate"
          >
            使用模板
          </el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Document, Position, RefreshRight,
  DArrowRight, UploadFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 表单引用
const messageFormRef = ref()
const uploadRef = ref()

// 响应式数据
const sending = ref(false)
const templateDialogVisible = ref(false)
const selectedTemplate = ref(null)
const fileList = ref([])

// 表单数据
const messageForm = reactive({
  recipient: '',
  subject: '',
  content: '',
  options: []
})

// 表单验证规则
const formRules = {
  recipient: [
    { required: true, message: '请选择收件人', trigger: 'change' }
  ],
  subject: [
    { required: true, message: '请输入消息主题', trigger: 'blur' },
    { min: 2, max: 100, message: '主题长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入消息内容', trigger: 'blur' },
    { min: 5, max: 2000, message: '内容长度在 5 到 2000 个字符', trigger: 'blur' }
  ]
}

// 联系人列表
const contacts = ref([
  { id: 1, name: '张同学', type: '同学' },
  { id: 2, name: '李老师', type: '教师' },
  { id: 3, name: '王同学', type: '同学' },
  { id: 4, name: '赵教授', type: '教师' },
  { id: 5, name: '陈同学', type: '同学' },
  { id: 6, name: '刘老师', type: '教师' }
])

// 消息模板
const messageTemplates = [
  {
    id: 1,
    title: '作业提交',
    preview: '老师您好，我已完成作业...',
    content: '尊敬的老师，\n\n我已完成您布置的作业，现提交给您查阅。如有不当之处，请指正。\n\n谢谢您的指导！\n\n学生敬上'
  },
  {
    id: 2,
    title: '请假申请',
    preview: '因为身体不适，申请请假...',
    content: '尊敬的老师，\n\n因为身体不适，申请请假一天。课程内容我会找同学补习，不会影响学习进度。\n\n请批准，谢谢！\n\n学生敬上'
  },
  {
    id: 3,
    title: '学习交流',
    preview: '想和您讨论一下课程问题...',
    content: '同学你好，\n\n想和您讨论一下最近学习的课程内容，有几个问题想请教。有时间的话我们可以一起学习交流。\n\n期待您的回复！'
  },
  {
    id: 4,
    title: '活动邀请',
    preview: '邀请您参加学习活动...',
    content: '同学你好，\n\n我们正在组织一个学习交流活动，时间是本周末，地点在图书馆。邀请您参加，大家可以一起讨论学习心得。\n\n如果有兴趣，请回复确认！'
  }
]

// 方法
const initializeFromQuery = () => {
  // 从路由查询参数初始化表单
  if (route.query.to) {
    messageForm.recipient = route.query.to
  }
  if (route.query.subject) {
    messageForm.subject = route.query.subject
  }
  if (route.query.content) {
    messageForm.content = route.query.content
  }
}

const insertFormat = (format) => {
  // 简单的格式插入功能
  ElMessage.info('格式功能开发中...')
}

const insertTemplate = () => {
  templateDialogVisible.value = true
  selectedTemplate.value = null
}

const selectTemplate = (template) => {
  selectedTemplate.value = template
}

const applyTemplate = () => {
  if (selectedTemplate.value) {
    messageForm.content = selectedTemplate.value.content
    templateDialogVisible.value = false
    ElMessage.success('模板已应用')
  }
}

const handleFileChange = (file, fileList) => {
  // 检查文件大小
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  
  fileList.value = fileList
}

const handleFileRemove = (file, fileList) => {
  fileList.value = fileList
}

const sendMessage = async () => {
  try {
    const valid = await messageFormRef.value.validate()
    if (!valid) return

    sending.value = true

    // 模拟发送消息
    await new Promise(resolve => setTimeout(resolve, 2000))

    ElMessage.success('消息发送成功！')
    
    // 重置表单并返回
    resetForm()
    router.push('/messages')
    
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('消息发送失败，请重试')
  } finally {
    sending.value = false
  }
}

const saveDraft = async () => {
  try {
    // 模拟保存草稿
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('草稿已保存')
  } catch (error) {
    console.error('保存草稿失败:', error)
    ElMessage.error('保存草稿失败')
  }
}

const resetForm = async () => {
  try {
    await ElMessageBox.confirm('确定要重置表单吗？所有内容将被清除。', '确认重置', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    messageFormRef.value.resetFields()
    fileList.value = []
    ElMessage.success('表单已重置')
  } catch {
    ElMessage.info('已取消重置')
  }
}

// 组件挂载
onMounted(() => {
  initializeFromQuery()
})
</script>

<style lang="scss" scoped>
.compose-message {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  
  h1 {
    margin: 0;
    color: var(--text-color-primary);
  }
}

.compose-container {
  max-width: 800px;
  margin: 0 auto;
}

.compose-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.editor-container {
  .editor-toolbar {
    margin-bottom: 12px;
    padding: 8px;
    background-color: var(--fill-color-lighter);
    border-radius: 4px;
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}

.template-card {
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  &.selected {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px var(--color-primary-light-7);
  }
  
  h4 {
    margin: 0 0 8px 0;
    color: var(--text-color-primary);
  }
  
  .template-preview {
    margin: 0;
    font-size: 14px;
    color: var(--text-color-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

:deep(.el-upload-dragger) {
  padding: 30px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

@media (max-width: 768px) {
  .compose-message {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    
    h1 {
      text-align: center;
    }
  }
  
  .form-actions {
    flex-direction: column;
    
    .el-button {
      width: 100%;
    }
  }
}
</style> 